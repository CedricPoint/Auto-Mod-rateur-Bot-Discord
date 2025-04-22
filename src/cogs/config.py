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

    @commands.command(name="set_stats_channel")
    @commands.has_permissions(administrator=True)
    async def set_stats_channel(self, ctx, stat_type: str, channel: discord.VoiceChannel = None):
        """Configure un salon pour les statistiques
        Types disponibles: members, bots, total, channels, roles
        Exemple: ?set_stats_channel members #salon
        Pour désactiver: ?set_stats_channel members"""
        
        valid_types = ["members", "bots", "total", "channels", "roles"]
        if stat_type not in valid_types:
            await ctx.send(f"❌ Type invalide. Types disponibles : {', '.join(valid_types)}")
            return
            
        # Si aucun salon n'est spécifié, on désactive le compteur
        if channel is None:
            self.config["stats_channels"][stat_type] = None
            save_config(self.config)
            await ctx.send(f"✅ Compteur {stat_type} désactivé.")
            return
            
        self.config["stats_channels"][stat_type] = channel.id
        save_config(self.config)
        
        # Mise à jour immédiate du compteur
        await self._update_stats_channel(stat_type)
        
        embed = discord.Embed(
            title="✅ Compteur Configuré",
            description=f"Le compteur {stat_type} a été configuré dans le salon {channel.mention}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Par {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command(name="set_stats_format")
    @commands.has_permissions(administrator=True)
    async def set_stats_format(self, ctx, stat_type: str, *, format_text: str):
        """Configure le format d'affichage d'un compteur
        Types disponibles: members, bots, total, channels, roles
        Utilisez {count} pour le nombre
        Exemple: ?set_stats_format members 👥 Membres : {count}"""
        
        valid_types = ["members", "bots", "total", "channels", "roles"]
        if stat_type not in valid_types:
            await ctx.send(f"❌ Type invalide. Types disponibles : {', '.join(valid_types)}")
            return
            
        if "{count}" not in format_text:
            await ctx.send("❌ Le format doit contenir {count}")
            return
            
        self.config["stats_format"][stat_type] = format_text
        save_config(self.config)
        
        # Mise à jour immédiate du compteur
        await self._update_stats_channel(stat_type)
        
        embed = discord.Embed(
            title="✅ Format Configuré",
            description=f"Le format du compteur {stat_type} a été mis à jour",
            color=discord.Color.green()
        )
        embed.add_field(name="Nouveau format", value=f"`{format_text}`")
        embed.set_footer(text=f"Par {ctx.author}")
        await ctx.send(embed=embed)

    async def _update_stats_channel(self, stat_type: str):
        """Met à jour un salon de statistiques"""
        channel_id = self.config["stats_channels"][stat_type]
        if not channel_id:
            return
            
        channel = self.bot.get_channel(channel_id)
        if not channel:
            return
            
        guild = channel.guild
        count = 0
        
        if stat_type == "members":
            count = len([m for m in guild.members if not m.bot])
        elif stat_type == "bots":
            count = len([m for m in guild.members if m.bot])
        elif stat_type == "total":
            count = len(guild.members)
        elif stat_type == "channels":
            count = len(guild.channels)
        elif stat_type == "roles":
            count = len(guild.roles)
            
        new_name = self.config["stats_format"][stat_type].format(count=count)
        
        try:
            await channel.edit(name=new_name)
        except discord.Forbidden:
            self.bot.logger.error(f"Impossible de modifier le nom du salon {channel.name}")
        except discord.HTTPException as e:
            self.bot.logger.error(f"Erreur lors de la modification du salon {channel.name}: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Met à jour les compteurs quand un membre rejoint"""
        for stat_type in ["members", "bots", "total"]:
            await self._update_stats_channel(stat_type)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Met à jour les compteurs quand un membre part"""
        for stat_type in ["members", "bots", "total"]:
            await self._update_stats_channel(stat_type)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Met à jour le compteur de salons quand un salon est créé"""
        await self._update_stats_channel("channels")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Met à jour le compteur de salons quand un salon est supprimé"""
        await self._update_stats_channel("channels")

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        """Met à jour le compteur de rôles quand un rôle est créé"""
        await self._update_stats_channel("roles")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """Met à jour le compteur de rôles quand un rôle est supprimé"""
        await self._update_stats_channel("roles")

    @commands.command(name="setup_stats")
    @commands.has_permissions(administrator=True)
    async def setup_stats(self, ctx):
        """Crée et configure automatiquement tous les compteurs de statistiques"""
        try:
            # Création de la catégorie
            category = await ctx.guild.create_category(
                "📊 STATISTIQUES",
                position=0  # En haut du serveur
            )

            # Création des salons vocaux pour chaque statistique
            stats_channels = {
                "total": "📊 Total : {count}",
                "members": "👥 Membres : {count}",
                "bots": "🤖 Bots : {count}",
                "channels": "📝 Salons : {count}",
                "roles": "🎭 Rôles : {count}"
            }

            progress_msg = await ctx.send("⏳ Création des compteurs en cours...")

            for stat_type, format_text in stats_channels.items():
                # Création du salon vocal
                channel = await ctx.guild.create_voice_channel(
                    name=format_text.format(count=0),
                    category=category
                )
                
                # Configuration du compteur
                self.config["stats_channels"][stat_type] = channel.id
                self.config["stats_format"][stat_type] = format_text
                
                # Mise à jour immédiate du compteur
                await self._update_stats_channel(stat_type)

            # Sauvegarde de la configuration
            save_config(self.config)

            # Désactiver la possibilité de se connecter aux salons vocaux
            for channel in category.voice_channels:
                await channel.set_permissions(ctx.guild.default_role, connect=False)

            embed = discord.Embed(
                title="✅ Compteurs Configurés",
                description="Les compteurs de statistiques ont été créés et configurés avec succès !",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Catégorie créée",
                value=category.name,
                inline=False
            )
            embed.add_field(
                name="Compteurs créés",
                value="\n".join(f"• {name}" for name in stats_channels.values()),
                inline=False
            )
            embed.set_footer(text=f"Par {ctx.author}")

            await progress_msg.delete()
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas les permissions nécessaires pour créer les salons.")
        except Exception as e:
            await ctx.send(f"❌ Une erreur est survenue : {str(e)}")

    @commands.command(name="delete_stats")
    @commands.has_permissions(administrator=True)
    async def delete_stats(self, ctx):
        """Supprime tous les compteurs de statistiques"""
        try:
            progress_msg = await ctx.send("⏳ Suppression des compteurs en cours...")
            deleted_channels = []

            # Récupération de la catégorie STATISTIQUES
            stats_category = None
            for category in ctx.guild.categories:
                if category.name.upper() == "📊 STATISTIQUES":
                    stats_category = category
                    break

            # Suppression des salons vocaux
            for stat_type in self.config["stats_channels"]:
                channel_id = self.config["stats_channels"][stat_type]
                if channel_id:
                    channel = ctx.guild.get_channel(channel_id)
                    if channel:
                        await channel.delete()
                        deleted_channels.append(channel.name)
                    self.config["stats_channels"][stat_type] = None

            # Suppression de la catégorie si elle existe
            if stats_category:
                await stats_category.delete()

            # Sauvegarde de la configuration
            save_config(self.config)

            embed = discord.Embed(
                title="✅ Compteurs Supprimés",
                description="Les compteurs de statistiques ont été supprimés avec succès !",
                color=discord.Color.green()
            )
            if deleted_channels:
                embed.add_field(
                    name="Salons supprimés",
                    value="\n".join(f"• {name}" for name in deleted_channels),
                    inline=False
                )
            if stats_category:
                embed.add_field(
                    name="Catégorie supprimée",
                    value=stats_category.name,
                    inline=False
                )
            embed.set_footer(text=f"Par {ctx.author}")

            await progress_msg.delete()
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas les permissions nécessaires pour supprimer les salons.")
        except Exception as e:
            await ctx.send(f"❌ Une erreur est survenue : {str(e)}")

    @commands.command(name="delete_stat")
    @commands.has_permissions(administrator=True)
    async def delete_stat(self, ctx, stat_type: str):
        """Supprime un compteur spécifique
        Types disponibles: members, bots, total, channels, roles
        Exemple: ?delete_stat members"""
        
        valid_types = ["members", "bots", "total", "channels", "roles"]
        if stat_type not in valid_types:
            await ctx.send(f"❌ Type invalide. Types disponibles : {', '.join(valid_types)}")
            return

        try:
            # Récupération du salon
            channel_id = self.config["stats_channels"][stat_type]
            if not channel_id:
                await ctx.send(f"❌ Aucun compteur '{stat_type}' n'est configuré.")
                return

            channel = ctx.guild.get_channel(channel_id)
            if not channel:
                await ctx.send(f"❌ Le salon du compteur '{stat_type}' n'a pas été trouvé.")
                return

            # Suppression du salon
            channel_name = channel.name
            await channel.delete()
            
            # Mise à jour de la configuration
            self.config["stats_channels"][stat_type] = None
            save_config(self.config)

            # Vérification si la catégorie est vide
            if channel.category and not channel.category.channels:
                await channel.category.delete()
                category_deleted = True
            else:
                category_deleted = False

            embed = discord.Embed(
                title="✅ Compteur Supprimé",
                description=f"Le compteur '{stat_type}' a été supprimé avec succès !",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Salon supprimé",
                value=channel_name,
                inline=False
            )
            if category_deleted:
                embed.add_field(
                    name="Catégorie supprimée",
                    value="La catégorie a été supprimée car elle était vide.",
                    inline=False
                )
            embed.set_footer(text=f"Par {ctx.author}")
            
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas les permissions nécessaires pour supprimer le salon.")
        except Exception as e:
            await ctx.send(f"❌ Une erreur est survenue : {str(e)}")

async def setup(bot):
    await bot.add_cog(ConfigCog(bot)) 