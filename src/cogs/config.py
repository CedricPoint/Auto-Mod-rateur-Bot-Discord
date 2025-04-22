import discord
from discord.ext import commands
from src.utils.config import save_config

class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    @commands.command(name="set_owner")
    async def set_owner(self, ctx, user: discord.User):
        """Définit le propriétaire du bot"""
        # Vérifier si l'utilisateur est déjà propriétaire ou si c'est le premier propriétaire
        if self.config["owner_id"] is None or ctx.author.id == self.config["owner_id"]:
            self.config["owner_id"] = user.id
            save_config(self.config)
            
            embed = discord.Embed(
                title="👑 Propriétaire Défini",
                description=f"{user.mention} est maintenant le propriétaire du bot.",
                color=discord.Color.gold()
            )
            embed.set_footer(text="Auto Mod Bot")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("Vous n'avez pas les permissions nécessaires pour définir le propriétaire.")

    @commands.command(name="set_admin_role")
    async def set_admin_role(self, ctx, role: discord.Role):
        """Définit le rôle admin"""
        # Vérifier si l'utilisateur est propriétaire ou admin
        if ctx.author.id == self.config["owner_id"] or ctx.author.guild_permissions.administrator:
            self.config["admin_role_id"] = role.id
            save_config(self.config)
            
            embed = discord.Embed(
                title="🔧 Rôle Admin Défini",
                description=f"Le rôle {role.mention} a maintenant les permissions d'admin.",
                color=discord.Color.blue()
            )
            embed.set_footer(text="Auto Mod Bot")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("Vous n'avez pas les permissions nécessaires pour définir le rôle admin.")

    @commands.command(name="set_status")
    @commands.is_owner()
    async def set_status(self, ctx, *, status: str):
        """Définit le statut du bot"""
        self.config["status"] = status
        save_config(self.config)
        
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=status
            )
        )
        
        embed = discord.Embed(
            title="🔄 Statut Modifié",
            description=f"Le statut du bot a été mis à jour : {status}",
            color=discord.Color.green()
        )
        embed.set_footer(text="Auto Mod Bot")
        
        await ctx.send(embed=embed)

    @commands.command(name="add_banned_word")
    @commands.has_permissions(administrator=True)
    async def add_banned_word(self, ctx, *, word: str):
        """Ajoute un mot à la liste des mots interdits"""
        word = word.lower()
        if word in self.config["banned_words"]:
            await ctx.send(f"Le mot '{word}' est déjà dans la liste des mots interdits.")
            return
        
        self.config["banned_words"].append(word)
        save_config(self.config)
        
        embed = discord.Embed(
            title="✅ Mot Ajouté",
            description=f"Le mot '{word}' a été ajouté à la liste des mots interdits.",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Par {ctx.author}")
        
        await ctx.send(embed=embed)

    @commands.command(name="remove_banned_word")
    @commands.has_permissions(administrator=True)
    async def remove_banned_word(self, ctx, *, word: str):
        """Retire un mot de la liste des mots interdits"""
        word = word.lower()
        if word not in self.config["banned_words"]:
            await ctx.send(f"Le mot '{word}' n'est pas dans la liste des mots interdits.")
            return
        
        self.config["banned_words"].remove(word)
        save_config(self.config)
        
        embed = discord.Embed(
            title="❌ Mot Retiré",
            description=f"Le mot '{word}' a été retiré de la liste des mots interdits.",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Par {ctx.author}")
        
        await ctx.send(embed=embed)

    @commands.command(name="list_banned_words")
    @commands.has_permissions(administrator=True)
    async def list_banned_words(self, ctx):
        """Affiche la liste des mots interdits"""
        if not self.config["banned_words"]:
            await ctx.send("Aucun mot n'est actuellement interdit.")
            return
        
        words_list = "\n".join(f"• {word}" for word in self.config["banned_words"])
        embed = discord.Embed(
            title="📝 Mots Interdits",
            description=words_list,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Auto Mod Bot")
        
        await ctx.send(embed=embed)

    @commands.command(name="set_log_channel")
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx, channel: discord.TextChannel):
        """Définit le canal de logs"""
        self.config["log_channel_id"] = channel.id
        save_config(self.config)
        
        embed = discord.Embed(
            title="📝 Canal de Logs Défini",
            description=f"Le canal de logs a été défini sur {channel.mention}",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Auto Mod Bot")
        
        await ctx.send(embed=embed)

    @commands.command(name="list_banned_files")
    async def list_banned_files(self, ctx):
        """Affiche la liste des extensions de fichiers interdites"""
        extensions = self.config["banned_extensions"]
        
        embed = discord.Embed(
            title="📁 Extensions de Fichiers Interdites",
            description="Voici la liste des extensions de fichiers qui ne sont pas autorisées :",
            color=discord.Color.blue()
        )
        
        extensions_list = "\n".join(f"• `{ext}`" for ext in extensions)
        embed.add_field(name="Extensions", value=extensions_list)
        embed.set_footer(text="Auto Mod Bot")
        
        await ctx.send(embed=embed)

    @commands.command(name="add_auto_reaction")
    @commands.has_permissions(administrator=True)
    async def add_auto_reaction(self, ctx, channel: discord.TextChannel, *, emoji: str):
        """Ajoute une réaction automatique à un salon
        Exemple: ?add_auto_reaction #général 👍
        Pour les emojis personnalisés: ?add_auto_reaction #général :nom_emoji:
        """
        # Nettoyer l'emoji des espaces
        emoji = emoji.strip()
        
        # Vérifier si l'emoji est valide
        try:
            # Si c'est un emoji personnalisé (format <:name:id>)
            if emoji.startswith('<') and emoji.endswith('>'):
                emoji_id = emoji.split(':')[-1][:-1]
                custom_emoji = self.bot.get_emoji(int(emoji_id))
                if custom_emoji is None:
                    await ctx.send("❌ Emoji personnalisé non trouvé. Assurez-vous que le bot a accès à cet emoji.")
                    return
                emoji = str(custom_emoji)
            # Tester l'emoji
            await ctx.message.add_reaction(emoji)
        except (discord.HTTPException, ValueError):
            await ctx.send("❌ Emoji invalide. Veuillez utiliser un emoji standard ou un emoji personnalisé du serveur.")
            return
            
        channel_id = str(channel.id)
        
        # Initialiser la liste des réactions si elle n'existe pas
        if channel_id not in self.config["auto_reactions"]:
            self.config["auto_reactions"][channel_id] = []
            
        if emoji in self.config["auto_reactions"][channel_id]:
            await ctx.send(f"L'emoji {emoji} est déjà configuré pour ce salon.")
            return
            
        self.config["auto_reactions"][channel_id].append(emoji)
        save_config(self.config)
        
        embed = discord.Embed(
            title="✅ Réaction Ajoutée",
            description=f"L'emoji {emoji} sera maintenant ajouté automatiquement aux messages dans {channel.mention}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Par {ctx.author}")
        
        await ctx.send(embed=embed)

    @commands.command(name="remove_auto_reaction")
    @commands.has_permissions(administrator=True)
    async def remove_auto_reaction(self, ctx, channel: discord.TextChannel, *, emoji: str):
        """Retire une réaction automatique d'un salon
        Exemple: ?remove_auto_reaction #général 👍
        Pour les emojis personnalisés: ?remove_auto_reaction #général :nom_emoji:
        """
        # Nettoyer l'emoji des espaces
        emoji = emoji.strip()
        
        # Gérer les emojis personnalisés
        if emoji.startswith('<') and emoji.endswith('>'):
            emoji_id = emoji.split(':')[-1][:-1]
            custom_emoji = self.bot.get_emoji(int(emoji_id))
            if custom_emoji is not None:
                emoji = str(custom_emoji)
        
        channel_id = str(channel.id)
        
        if channel_id not in self.config["auto_reactions"] or emoji not in self.config["auto_reactions"][channel_id]:
            await ctx.send(f"L'emoji {emoji} n'est pas configuré pour ce salon.")
            return
            
        self.config["auto_reactions"][channel_id].remove(emoji)
        if not self.config["auto_reactions"][channel_id]:
            del self.config["auto_reactions"][channel_id]
            
        save_config(self.config)
        
        embed = discord.Embed(
            title="❌ Réaction Retirée",
            description=f"L'emoji {emoji} ne sera plus ajouté automatiquement aux messages dans {channel.mention}",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Par {ctx.author}")
        
        await ctx.send(embed=embed)

    @commands.command(name="list_auto_reactions")
    @commands.has_permissions(administrator=True)
    async def list_auto_reactions(self, ctx):
        """Affiche la liste des réactions automatiques configurées"""
        if not self.config["auto_reactions"]:
            await ctx.send("Aucune réaction automatique n'est configurée.")
            return
            
        embed = discord.Embed(
            title="📝 Réactions Automatiques",
            description="Voici la liste des réactions automatiques configurées :",
            color=discord.Color.blue()
        )
        
        for channel_id, emojis in self.config["auto_reactions"].items():
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                embed.add_field(
                    name=f"#{channel.name}",
                    value=" ".join(emojis),
                    inline=False
                )
        
        embed.set_footer(text="Auto Mod Bot")
        await ctx.send(embed=embed)

    @commands.command(name="set_welcome_channel")
    @commands.has_permissions(administrator=True)
    async def set_welcome_channel(self, ctx, channel: discord.TextChannel):
        """Définit le salon pour les messages de bienvenue et d'au revoir
        Exemple: ?set_welcome_channel #bienvenue
        """
        self.config["welcome_channel_id"] = channel.id
        save_config(self.config)
        
        embed = discord.Embed(
            title="✅ Salon de Bienvenue Défini",
            description=f"Les messages de bienvenue et d'au revoir seront envoyés dans {channel.mention}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Par {ctx.author}")
        
        await ctx.send(embed=embed)

    @commands.command(name="set_welcome_message")
    @commands.has_permissions(administrator=True)
    async def set_welcome_message(self, ctx, *, message: str):
        """Définit le message de bienvenue
        Variables disponibles: {member.mention}, {member.name}, {member_count}
        Exemple: ?set_welcome_message Bienvenue {member.mention} sur le serveur ! 🎉 Nous sommes maintenant {member_count} membres !
        """
        self.config["welcome_message"] = message
        save_config(self.config)
        
        # Créer un exemple avec les variables remplacées
        example = message.format(
            member=ctx.author,
            member_count=len(ctx.guild.members)
        )
        
        embed = discord.Embed(
            title="✅ Message de Bienvenue Défini",
            description="Nouveau message configuré :",
            color=discord.Color.green()
        )
        embed.add_field(name="Format", value=f"```{message}```", inline=False)
        embed.add_field(name="Exemple", value=example, inline=False)
        embed.set_footer(text=f"Par {ctx.author}")
        
        await ctx.send(embed=embed)

    @commands.command(name="set_goodbye_message")
    @commands.has_permissions(administrator=True)
    async def set_goodbye_message(self, ctx, *, message: str):
        """Définit le message d'au revoir
        Variables disponibles: {member.name}, {member_count}
        Exemple: ?set_goodbye_message Au revoir {member.name} ! 😢 Nous sommes maintenant {member_count} membres.
        """
        self.config["goodbye_message"] = message
        save_config(self.config)
        
        # Créer un exemple avec les variables remplacées
        example = message.format(
            member=ctx.author,
            member_count=len(ctx.guild.members)
        )
        
        embed = discord.Embed(
            title="✅ Message d'Au Revoir Défini",
            description="Nouveau message configuré :",
            color=discord.Color.green()
        )
        embed.add_field(name="Format", value=f"```{message}```", inline=False)
        embed.add_field(name="Exemple", value=example, inline=False)
        embed.set_footer(text=f"Par {ctx.author}")
        
        await ctx.send(embed=embed)

    @commands.command(name="show_welcome_config")
    @commands.has_permissions(administrator=True)
    async def show_welcome_config(self, ctx):
        """Affiche la configuration actuelle des messages de bienvenue et d'au revoir"""
        welcome_channel = self.bot.get_channel(self.config["welcome_channel_id"]) if self.config["welcome_channel_id"] else None
        
        embed = discord.Embed(
            title="📝 Configuration des Messages",
            description="Configuration actuelle des messages de bienvenue et d'au revoir",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Salon",
            value=welcome_channel.mention if welcome_channel else "Non configuré",
            inline=False
        )
        
        embed.add_field(
            name="Message de Bienvenue",
            value=f"```{self.config['welcome_message']}```",
            inline=False
        )
        
        embed.add_field(
            name="Message d'Au Revoir",
            value=f"```{self.config['goodbye_message']}```",
            inline=False
        )
        
        embed.set_footer(text="Auto Mod Bot")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ConfigCog(bot)) 