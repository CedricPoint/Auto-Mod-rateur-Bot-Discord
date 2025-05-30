import discord
from discord.ext import commands
import re
from datetime import datetime, timedelta
import random

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.warnings = {}  # Dictionnaire pour stocker les avertissements

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Message de bienvenue"""
        if self.config["welcome_channel_id"]:
            welcome_channel = self.bot.get_channel(self.config["welcome_channel_id"])
            if welcome_channel:
                # Calcul précis du nombre de membres
                real_members = len([m for m in member.guild.members if not m.bot])
                total_members = len(member.guild.members)
                
                self.bot.logger.info(f"Arrivée de {member.name}")
                self.bot.logger.info(f"Nombre total de membres (avec bots): {total_members}")
                self.bot.logger.info(f"Nombre de membres (sans bots): {real_members}")
                
                member_count = real_members
                welcome_message = self.config["welcome_message"].format(
                    member=member,
                    member_count=member_count
                )
                
                embed = discord.Embed(
                    title="👋 Nouveau Membre",
                    description=welcome_message,
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text="Auto Mod Bot")
                
                await welcome_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Message d'au revoir"""
        if self.config["welcome_channel_id"]:
            welcome_channel = self.bot.get_channel(self.config["welcome_channel_id"])
            if welcome_channel:
                # Calcul précis du nombre de membres
                real_members = len([m for m in member.guild.members if not m.bot])
                total_members = len(member.guild.members)
                
                self.bot.logger.info(f"Départ de {member.name}")
                self.bot.logger.info(f"Nombre total de membres (avec bots): {total_members}")
                self.bot.logger.info(f"Nombre de membres (sans bots): {real_members}")
                
                # On soustrait 1 car le membre a déjà quitté
                member_count = real_members - 1
                goodbye_message = self.config["goodbye_message"].format(
                    member=member,
                    member_count=member_count
                )
                
                embed = discord.Embed(
                    title="👋 Départ d'un Membre",
                    description=goodbye_message,
                    color=discord.Color.red()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text="Auto Mod Bot")
                
                await welcome_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        # Réactions automatiques configurées par salon
        channel_id = str(message.channel.id)
        if channel_id in self.config["auto_reactions"]:
            for emoji in self.config["auto_reactions"][channel_id]:
                try:
                    await message.add_reaction(emoji)
                except discord.Forbidden:
                    self.bot.logger.error(f"Impossible d'ajouter la réaction {emoji} au message de {message.author}")

        # Ne pas faire la modération sur les messages de bots
        if message.author.bot:
            return

        # Vérification des mots interdits
        message_content = message.content.lower()
        for word in self.config["banned_words"]:
            if re.search(rf'\b{word}\b', message_content):
                try:
                    await message.delete()
                    embed = discord.Embed(
                        title="⚠️ Message Supprimé",
                        description=f"{message.author.mention}, ce type de contenu n'est pas autorisé ici!",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Mot interdit détecté", value=word)
                    embed.set_footer(text="Auto Mod Bot")
                    await message.channel.send(embed=embed, delete_after=10)
                    
                    await self._log_action(
                        f"Message supprimé de {message.author} (ID: {message.author.id})\n"
                        f"Contenu: {message.content[:100]}...\n"
                        f"Mot interdit détecté: {word}"
                    )
                    
                    await self._add_warning(message.author)
                except discord.Forbidden:
                    self.bot.logger.error(f"Impossible de supprimer le message de {message.author}")
                return

        # Vérification des fichiers interdits
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in self.config["banned_extensions"]):
                try:
                    await message.delete()
                    embed = discord.Embed(
                        title="⚠️ Fichier Supprimé",
                        description=f"{message.author.mention}, l'upload de fichiers {attachment.filename.split('.')[-1]} n'est pas autorisé ici!",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Nom du fichier", value=attachment.filename)
                    embed.set_footer(text="Auto Mod Bot")
                    await message.channel.send(embed=embed, delete_after=10)
                    
                    await self._log_action(
                        f"Fichier supprimé de {message.author} (ID: {message.author.id})\n"
                        f"Nom du fichier: {attachment.filename}"
                    )
                    
                    await self._add_warning(message.author)
                except discord.Forbidden:
                    self.bot.logger.error(f"Impossible de supprimer le fichier de {message.author}")
                return

    async def _add_warning(self, member: discord.Member):
        """Ajoute un avertissement à un membre"""
        if member.id not in self.warnings:
            self.warnings[member.id] = []
        
        self.warnings[member.id].append(datetime.now())
        
        # Nettoyage des anciens avertissements
        self.warnings[member.id] = [
            w for w in self.warnings[member.id]
            if datetime.now() - w < timedelta(hours=self.config["warning_duration"])
        ]
        
        if len(self.warnings[member.id]) >= self.config["max_warnings"]:
            if self.config["auto_timeout"]:
                try:
                    await member.timeout(
                        timedelta(seconds=self.config["timeout_duration"]),
                        reason="Trop d'avertissements"
                    )
                    await self._log_action(
                        f"Timeout automatique pour {member} (ID: {member.id})\n"
                        f"Raison: Trop d'avertissements"
                    )
                except discord.Forbidden:
                    self.bot.logger.error(f"Impossible de mettre en timeout {member}")

    @commands.command(name="warn")
    @commands.has_permissions(administrator=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        """Donne un avertissement à un membre"""
        await self._add_warning(member)
        
        embed = discord.Embed(
            title="⚠️ Avertissement",
            description=f"{member.mention} a reçu un avertissement.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Raison", value=reason)
        embed.add_field(name="Avertissements", value=f"{len(self.warnings.get(member.id, []))}/{self.config['max_warnings']}")
        embed.set_footer(text=f"Par {ctx.author}")
        
        await ctx.send(embed=embed)
        await self._log_action(
            f"Avertissement donné à {member} (ID: {member.id})\n"
            f"Raison: {reason}\n"
            f"Par: {ctx.author}"
        )

    @commands.command(name="warnings")
    @commands.has_permissions(administrator=True)
    async def warnings(self, ctx, member: discord.Member):
        """Affiche les avertissements d'un membre"""
        member_warnings = self.warnings.get(member.id, [])
        
        embed = discord.Embed(
            title=f"⚠️ Avertissements de {member}",
            color=discord.Color.orange()
        )
        
        if member_warnings:
            warnings_list = "\n".join(
                f"• {w.strftime('%d/%m/%Y %H:%M')}"
                for w in member_warnings
            )
            embed.description = warnings_list
        else:
            embed.description = "Aucun avertissement"
        
        embed.add_field(
            name="Statut",
            value=f"{len(member_warnings)}/{self.config['max_warnings']} avertissements"
        )
        embed.set_footer(text="Auto Mod Bot")
        
        await ctx.send(embed=embed)

    @commands.command(name="clear")
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, amount: int):
        """Supprime un nombre spécifié de messages"""
        if amount <= 0 or amount > 100:
            await ctx.send("Veuillez spécifier un nombre entre 1 et 100.")
            return

        try:
            deleted = await ctx.channel.purge(limit=amount)
            embed = discord.Embed(
                title="🗑️ Messages Supprimés",
                description=f"{len(deleted)} messages ont été supprimés.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Par {ctx.author}")
            
            await ctx.send(embed=embed, delete_after=5)
            await self._log_action(
                f"{ctx.author} a supprimé {len(deleted)} messages dans {ctx.channel.mention}"
            )
        except discord.Forbidden:
            await ctx.send("Je n'ai pas les permissions nécessaires pour supprimer des messages.")

    @commands.command(name="react_history")
    @commands.has_permissions(administrator=True)
    async def react_history(self, ctx, channel: discord.TextChannel, limit: int = 100):
        """Ajoute les réactions configurées aux anciens messages du salon
        Exemple: ?react_history #salon 100"""
        channel_id = str(channel.id)
        if channel_id not in self.config["auto_reactions"]:
            await ctx.send("❌ Aucune réaction n'est configurée pour ce salon.")
            return

        if limit > 1000:
            await ctx.send("❌ La limite maximale est de 1000 messages.")
            return

        progress_msg = await ctx.send("⏳ Ajout des réactions en cours...")
        count = 0
        
        try:
            async for message in channel.history(limit=limit):
                for emoji in self.config["auto_reactions"][channel_id]:
                    try:
                        await message.add_reaction(emoji)
                        count += 1
                    except discord.Forbidden:
                        continue
                    except discord.NotFound:
                        continue
        except Exception as e:
            await progress_msg.edit(content=f"❌ Une erreur est survenue : {str(e)}")
            return

        embed = discord.Embed(
            title="✅ Réactions Ajoutées",
            description=f"J'ai ajouté {count} réactions aux {limit} derniers messages dans {channel.mention}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Par {ctx.author}")
        
        await progress_msg.delete()
        await ctx.send(embed=embed)

    @commands.command(name="clearwarns")
    @commands.has_permissions(administrator=True)
    async def clearwarns(self, ctx, member: discord.Member):
        """Supprime tous les avertissements d'un membre"""
        if member.id in self.warnings:
            old_count = len(self.warnings[member.id])
            self.warnings[member.id] = []
            
            embed = discord.Embed(
                title="🗑️ Avertissements Supprimés",
                description=f"Les avertissements de {member.mention} ont été supprimés.",
                color=discord.Color.green()
            )
            embed.add_field(name="Avertissements supprimés", value=str(old_count))
            embed.set_footer(text=f"Par {ctx.author}")
            
            await ctx.send(embed=embed)
            await self._log_action(
                f"Avertissements supprimés pour {member} (ID: {member.id})\n"
                f"Nombre d'avertissements supprimés: {old_count}\n"
                f"Par: {ctx.author}"
            )
        else:
            embed = discord.Embed(
                title="ℹ️ Information",
                description=f"{member.mention} n'a aucun avertissement.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

    async def _log_action(self, message):
        if self.config["log_channel_id"]:
            log_channel = self.bot.get_channel(self.config["log_channel_id"])
            if log_channel:
                embed = discord.Embed(
                    title="📝 Action de Modération",
                    description=message,
                    color=discord.Color.blue()
                )
                embed.set_footer(text="Auto Mod Bot")
                await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ModerationCog(bot)) 