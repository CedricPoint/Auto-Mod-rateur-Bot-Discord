import discord
from discord.ext import commands
import json
import os
from datetime import datetime
import asyncio
import io
import re

class SetupMessageView(discord.ui.View):
    def __init__(self, category_info, timeout=120):
        super().__init__(timeout=timeout)
        self.category_info = category_info
        self.value = None
        self.message = None

    @discord.ui.button(label="Utiliser message par défaut", emoji="✅", style=discord.ButtonStyle.green)
    async def use_default(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = self.category_info['default_message']
        await interaction.response.send_message(f"✅ Message par défaut sélectionné pour {self.category_info['name']}", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Écrire message personnalisé", emoji="✏️", style=discord.ButtonStyle.blurple)
    async def custom_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"📝 Veuillez écrire votre message personnalisé pour {self.category_info['name']}", ephemeral=True)
        self.value = "waiting_for_message"
        self.stop()

    async def on_timeout(self):
        self.value = self.category_info['default_message']
        if self.message:
            try:
                await self.message.edit(view=None)
            except:
                pass

class TicketsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tickets_file = 'data/tickets.json'
        self.tickets_data = self.load_tickets()
        self.current_context = None  # Pour stocker le contexte actuel
        
        # Créer le dossier data s'il n'existe pas
        os.makedirs('data', exist_ok=True)

        # Définition des priorités et leurs couleurs
        self.priorities = {
            "basse": {"color": discord.Color.green(), "emoji": "🟢"},
            "moyenne": {"color": discord.Color.yellow(), "emoji": "🟡"},
            "haute": {"color": discord.Color.orange(), "emoji": "🟠"},
            "urgente": {"color": discord.Color.red(), "emoji": "🔴"}
        }

        # Définition des catégories de tickets
        self.ticket_categories = {
            "support": {
                "emoji": "❓",
                "color": discord.Color.blue(),
                "name": "Support",
                "description": "Besoin d'aide ? Créez un ticket de support.",
                "default_message": "👋 Bienvenue {user} dans votre ticket de support !\n\n📝 Décrivez votre problème en détail pour que nous puissions mieux vous aider.\n\n⏳ Un membre du staff vous répondra dès que possible."
            },
            "bug": {
                "emoji": "🐛",
                "color": discord.Color.red(),
                "name": "Bug",
                "description": "Signalez un bug ou un problème technique.",
                "default_message": "🔍 Bonjour {user} !\n\n❗ Pour nous aider à résoudre le bug, merci de fournir :\n• Une description détaillée\n• Les étapes pour reproduire le bug\n• Des captures d'écran si possible\n\n⏳ Notre équipe technique examinera votre signalement."
            },
            "commande": {
                "emoji": "🛒",
                "color": discord.Color.green(),
                "name": "Commande",
                "description": "Passez une commande ou demandez un devis.",
                "default_message": "🛍️ Bienvenue {user} dans votre ticket de commande !\n\n📋 Merci de préciser :\n• Le produit/service souhaité\n• Vos besoins spécifiques\n• Votre budget si possible\n\n💼 Un conseiller vous accompagnera dans votre demande."
            },
            "autre": {
                "emoji": "💭",
                "color": discord.Color.greyple(),
                "name": "Autre",
                "description": "Autre demande ne correspondant pas aux catégories ci-dessus.",
                "default_message": "👋 Bonjour {user} !\n\n💬 Expliquez-nous en quoi nous pouvons vous aider.\n\n⏳ Un membre de l'équipe vous répondra dès que possible."
            }
        }

    def load_tickets(self):
        default_data = {
            'ticket_configs': {},  # Configurations par salon
            'active_tickets': {},
            'log_channel_id': None,
            'ticket_stats': {
                'total_tickets': 0,
                'tickets_by_category': {
                    'support': 0,
                    'bug': 0,
                    'commande': 0,
                    'autre': 0
                },
                'tickets_by_priority': {
                    'basse': 0,
                    'moyenne': 0,
                    'haute': 0,
                    'urgente': 0
                }
            }
        }
        
        if os.path.exists(self.tickets_file):
            try:
                with open(self.tickets_file, 'r') as f:
                    data = json.load(f)
                    # Migration des anciennes données
                    if 'ticket_category_id' in data:
                        # Créer une configuration par défaut avec les anciennes données
                        default_config = {
                            'category_id': data.get('ticket_category_id'),
                            'support_role_id': data.get('support_role_id'),
                            'welcome_message': "Bienvenue {user} dans votre ticket!\nUn membre du staff vous répondra dès que possible."
                        }
                        # Ajouter la configuration par défaut si elle existe
                        if default_config['category_id'] is not None:
                            default_data['ticket_configs']['default'] = default_config
                    
                    # Fusionner les données existantes avec la structure par défaut
                    for key in default_data:
                        if key not in data:
                            data[key] = default_data[key]
                    
                    return data
            except (json.JSONDecodeError, IOError):
                self.bot.logger.error("Erreur lors du chargement du fichier tickets.json")
                return default_data
        return default_data

    def save_tickets(self):
        with open(self.tickets_file, 'w') as f:
            json.dump(self.tickets_data, f, indent=4)

    @commands.command(name="ticket_setup")
    @commands.has_permissions(administrator=True)
    async def ticket_setup(self, ctx, channel: discord.TextChannel = None):
        """Lance l'assistant de configuration des tickets"""
        if channel is None:
            channel = ctx.channel

        # Vérifier si le salon a déjà une configuration
        if str(channel.id) in self.tickets_data['ticket_configs']:
            embed = discord.Embed(
                title="⚠️ Configuration existante",
                description="Ce salon a déjà une configuration de tickets.\nVoulez-vous la remplacer ?",
                color=discord.Color.orange()
            )
            view = discord.ui.View(timeout=60)
            view.add_item(discord.ui.Button(style=discord.ButtonStyle.danger, label="Remplacer", custom_id="replace_config"))
            view.add_item(discord.ui.Button(style=discord.ButtonStyle.secondary, label="Annuler", custom_id="cancel_config"))
            await ctx.send(embed=embed, view=view)
            return

        await self.start_setup_wizard(ctx, channel)

    async def start_setup_wizard(self, ctx, channel):
        """Lance l'assistant de configuration étape par étape"""
        config_data = {}
        
        # Étape 1: Configuration du rôle support
        embed = discord.Embed(
            title="🔧 Configuration des Tickets (1/3)",
            description="Mentionnez le rôle qui aura accès à tous les tickets\n"
                      "Par exemple: @Support ou @Staff",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

        try:
            support_role_msg = await self.bot.wait_for(
                'message',
                timeout=60.0,
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel and len(m.role_mentions) > 0
            )
            support_role = support_role_msg.role_mentions[0]
            config_data['support_role_id'] = support_role.id

            # Étape 2: Configuration des messages par catégorie
            embed = discord.Embed(
                title="🔧 Configuration des Tickets (2/3)",
                description="Configurons maintenant les messages de bienvenue pour chaque catégorie.\n"
                          "Vous pouvez utiliser {user} pour mentionner l'utilisateur.\n"
                          "Pour chaque catégorie, vous pouvez :\n"
                          "• Utiliser le message par défaut (✅)\n"
                          "• Écrire un message personnalisé (✏️)",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

            config_data['categories'] = {}
            for category_id, category_info in self.ticket_categories.items():
                embed = discord.Embed(
                    title=f"Message pour {category_info['name']} {category_info['emoji']}",
                    description=f"Message par défaut :\n```{category_info['default_message']}```\n"
                              f"Choisissez une option ci-dessous :",
                    color=category_info['color']
                )

                view = SetupMessageView(category_info)
                view.message = await ctx.send(embed=embed, view=view)
                
                # Attendre la réponse du view
                await view.wait()
                
                if view.value == "waiting_for_message":
                    try:
                        custom_msg = await self.bot.wait_for(
                            'message',
                            timeout=120.0,
                            check=lambda m: m.author == ctx.author and m.channel == ctx.channel
                        )
                        welcome_message = custom_msg.content
                        await ctx.send(f"✅ Message personnalisé enregistré pour {category_info['name']}", delete_after=5)
                    except asyncio.TimeoutError:
                        welcome_message = category_info['default_message']
                        await ctx.send(f"⏳ Temps écoulé, utilisation du message par défaut pour {category_info['name']}", delete_after=5)
                else:
                    welcome_message = view.value

                # Créer la catégorie Discord
                category_name = f"Tickets - {category_info['name']}"
                discord_category = await ctx.guild.create_category(category_name)
                
                config_data['categories'][category_id] = {
                    'welcome_message': welcome_message,
                    'category_id': discord_category.id
                }

                await asyncio.sleep(1)  # Petit délai pour la lisibilité

            # Étape 3: Salon des logs
            if not self.tickets_data['log_channel_id']:
                embed = discord.Embed(
                    title="🔧 Configuration des Tickets (3/3)",
                    description="Mentionnez le salon où seront envoyés les logs des tickets\n"
                              "Par exemple: #ticket-logs",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)

                log_channel_msg = await self.bot.wait_for(
                    'message',
                    timeout=60.0,
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel and len(m.channel_mentions) > 0
                )
                log_channel = log_channel_msg.channel_mentions[0]
                self.tickets_data['log_channel_id'] = log_channel.id

            # Étape 3: Création du message avec les boutons
            embed = discord.Embed(
                title="🎫 Création de Ticket",
                description="Cliquez sur le bouton correspondant à votre besoin pour créer un ticket.",
                color=discord.Color.blue()
            )

            # Ajouter un champ pour chaque catégorie
            for category_id, category_info in self.ticket_categories.items():
                embed.add_field(
                    name=f"{category_info['emoji']} {category_info['name']}",
                    value=category_info['description'],
                    inline=False
                )

            view = discord.ui.View(timeout=None)
            for category_id, category_info in self.ticket_categories.items():
                button = discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label=category_info['name'],
                    emoji=category_info['emoji'],
                    custom_id=f"create_ticket:{channel.id}:{category_id}"
                )
                view.add_item(button)

            setup_message = await channel.send(embed=embed, view=view)

            # Sauvegarder la configuration
            self.tickets_data['ticket_configs'][str(channel.id)] = {
                'support_role_id': config_data['support_role_id'],
                'categories': config_data['categories'],
                'setup_message_id': setup_message.id
            }
            self.save_tickets()

            # Message de confirmation
            embed = discord.Embed(
                title="✅ Configuration terminée",
                description=f"Le système de tickets a été configuré avec succès dans {channel.mention}.\n"
                          f"Rôle support : <@&{config_data['support_role_id']}>",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

        except asyncio.TimeoutError:
            await ctx.send("❌ Configuration annulée : temps écoulé.")
            return

    @commands.command(name="close")
    async def close_ticket(self, ctx):
        """Ferme le ticket actuel"""
        # Vérifier si le salon est un ticket en cherchant dans les tickets actifs
        is_ticket = False
        for user_id, ticket_data in self.tickets_data['active_tickets'].items():
            if ticket_data['channel_id'] == ctx.channel.id:
                is_ticket = True
                break

        if not is_ticket:
            await ctx.send("❌ Ce salon n'est pas un ticket!")
            return

        self.current_context = ctx

        embed = discord.Embed(
            title="🔒 Fermeture du Ticket",
            description="Êtes-vous sûr de vouloir fermer ce ticket?\n"
                      "Une transcription sera générée avant la fermeture.",
            color=discord.Color.orange()
        )

        view = discord.ui.View(timeout=None)
        confirm_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Confirmer",
            emoji="✅",
            custom_id=f"confirm_close:{ctx.channel.id}"
        )
        cancel_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Annuler",
            emoji="❌",
            custom_id=f"cancel_close:{ctx.channel.id}"
        )
        view.add_item(confirm_button)
        view.add_item(cancel_button)
        
        await ctx.send(embed=embed, view=view)

    @commands.command(name="ticket_list")
    @commands.has_permissions(administrator=True)
    async def ticket_list(self, ctx):
        """Liste toutes les configurations de tickets"""
        if not self.tickets_data['ticket_configs']:
            await ctx.send("❌ Aucune configuration de tickets n'existe.")
            return

        embed = discord.Embed(
            title="📋 Configurations des Tickets",
            description="Liste de tous les panneaux de tickets configurés",
            color=discord.Color.blue()
        )

        for channel_id, config in self.tickets_data['ticket_configs'].items():
            channel = ctx.guild.get_channel(int(channel_id))
            support_role = ctx.guild.get_role(config['support_role_id'])

            if channel and support_role:
                # Créer une liste des catégories configurées
                categories_info = []
                for cat_id, cat_config in config['categories'].items():
                    cat_channel = ctx.guild.get_channel(cat_config['category_id'])
                    cat_info = self.ticket_categories[cat_id]
                    if cat_channel:
                        categories_info.append(
                            f"• {cat_info['emoji']} {cat_info['name']} ({cat_channel.name})"
                        )

                embed.add_field(
                    name=f"📬 Configuration dans {channel.name}",
                    value=f"**Rôle Support:** {support_role.mention}\n"
                          f"**Catégories configurées:**\n" +
                          "\n".join(categories_info) +
                          f"\n**ID:** `{channel_id}`",
                    inline=False
                )

        # Ajouter les statistiques
        if self.tickets_data['ticket_stats']['total_tickets'] > 0:
            stats = self.tickets_data['ticket_stats']['tickets_by_category']
            stats_text = "\n".join([
                f"{self.ticket_categories[cat_id]['emoji']} **{self.ticket_categories[cat_id]['name']}:** {count} tickets"
                for cat_id, count in stats.items()
            ])
            
            embed.add_field(
                name="📊 Statistiques Globales",
                value=f"**Total des tickets:** {self.tickets_data['ticket_stats']['total_tickets']}\n{stats_text}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="ticket_delete")
    @commands.has_permissions(administrator=True)
    async def ticket_delete(self, ctx, channel: discord.TextChannel):
        """Supprime une configuration de tickets"""
        self.current_context = ctx  # Sauvegarder le contexte
        channel_id = str(channel.id)
        if channel_id not in self.tickets_data['ticket_configs']:
            await ctx.send("❌ Aucune configuration trouvée pour ce salon.")
            return

        config = self.tickets_data['ticket_configs'][channel_id]
        
        # Récupérer les informations de la configuration
        support_role = ctx.guild.get_role(config['support_role_id']) if config.get('support_role_id') else None
        categories_info = []
        
        for cat_id, cat_config in config['categories'].items():
            cat_channel = ctx.guild.get_channel(cat_config['category_id'])
            if cat_channel:
                categories_info.append(f"• {cat_channel.name}")

        embed = discord.Embed(
            title="⚠️ Confirmation de Suppression",
            description=f"Voulez-vous vraiment supprimer la configuration de tickets dans {channel.mention} ?\n\n"
                      f"**Catégories configurées:**\n" + "\n".join(categories_info) + "\n"
                      f"**Rôle Support:** {support_role.mention if support_role else 'Non configuré'}",
            color=discord.Color.red()
        )

        view = discord.ui.View(timeout=60)
        confirm_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Confirmer",
            custom_id=f"confirm_delete:{channel_id}"  # Ajout du channel_id dans le custom_id
        )
        cancel_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Annuler",
            custom_id=f"cancel_delete:{channel_id}"  # Ajout du channel_id dans le custom_id
        )
        view.add_item(confirm_button)
        view.add_item(cancel_button)

        await ctx.send(embed=embed, view=view)

    async def delete_after(self, interaction, delay=30):
        """Supprime un message après un délai donné"""
        await asyncio.sleep(delay)
        try:
            if isinstance(interaction, discord.Interaction):
                message = await interaction.original_response()
                await message.delete()
            else:
                await interaction.delete()
        except (discord.NotFound, discord.Forbidden):
            pass

    @commands.command(name="ticket_edit")
    @commands.has_permissions(administrator=True)
    async def ticket_edit(self, ctx, channel: discord.TextChannel):
        """Modifie une configuration de tickets existante"""
        self.current_context = ctx
        channel_id = str(channel.id)
        if channel_id not in self.tickets_data['ticket_configs']:
            await ctx.send("❌ Aucune configuration trouvée pour ce salon.")
            return

        config = self.tickets_data['ticket_configs'][channel_id]
        support_role = ctx.guild.get_role(config['support_role_id']) if config.get('support_role_id') else None

        embed = discord.Embed(
            title="🔧 Modification de la Configuration",
            description=f"Configuration actuelle pour {channel.mention}:\n\n"
                      f"**Rôle Support:** {support_role.mention if support_role else 'Non configuré'}\n\n"
                      "**Catégories configurées:**",
            color=discord.Color.blue()
        )

        view = discord.ui.View(timeout=120)

        # Ajouter un bouton pour modifier le rôle support
        view.add_item(discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Modifier le Rôle Support",
            emoji="👥",
            custom_id=f"edit_role:{channel_id}"
        ))

        # Ajouter un bouton pour chaque catégorie
        for cat_id, cat_config in config['categories'].items():
            cat_info = self.ticket_categories[cat_id]
            cat_channel = ctx.guild.get_channel(cat_config['category_id'])
            
            embed.add_field(
                name=f"{cat_info['emoji']} {cat_info['name']}",
                value=f"Catégorie: {cat_channel.name if cat_channel else 'Non trouvée'}\n"
                      f"Message: ```{cat_config.get('welcome_message', cat_info['default_message'])}```",
                inline=False
            )
            
            view.add_item(discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label=f"Modifier {cat_info['name']}",
                emoji=cat_info['emoji'],
                custom_id=f"edit_category:{channel_id}:{cat_id}"
            ))

        await ctx.send(embed=embed, view=view)

    async def handle_category_edit(self, interaction: discord.Interaction, channel_id: str, category_id: str = None):
        """Gère la modification d'une catégorie spécifique"""
        if interaction.user != self.current_context.author:
            await interaction.response.send_message("❌ Seul l'auteur de la commande peut utiliser ces boutons!", ephemeral=True)
            asyncio.create_task(self.delete_after(interaction))
            return

        config = self.tickets_data['ticket_configs'].get(channel_id)
        if not config:
            await interaction.response.send_message("❌ Configuration introuvable.", ephemeral=True)
            asyncio.create_task(self.delete_after(interaction))
            return

        cat_info = self.ticket_categories[category_id]
        cat_config = config['categories'][category_id]

        embed = discord.Embed(
            title=f"🔧 Modification de {cat_info['name']}",
            description="Que souhaitez-vous modifier ?",
            color=cat_info['color']
        )

        view = discord.ui.View(timeout=60)
        view.add_item(discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Modifier la Catégorie Discord",
            emoji="📁",
            custom_id=f"edit_cat_discord:{channel_id}:{category_id}"
        ))
        view.add_item(discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Modifier le Message",
            emoji="✏️",
            custom_id=f"edit_cat_message:{channel_id}:{category_id}"
        ))

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        asyncio.create_task(self.delete_after(interaction))

    async def handle_category_discord_edit(self, interaction: discord.Interaction, channel_id: str, category_id: str):
        """Gère la modification de la catégorie Discord"""
        await interaction.response.send_message("📝 Entrez le nom de la nouvelle catégorie Discord:", ephemeral=True)
        asyncio.create_task(self.delete_after(interaction))

        try:
            msg = await self.bot.wait_for(
                'message',
                timeout=60.0,
                check=lambda m: m.author == self.current_context.author and m.channel == self.current_context.channel
            )
            
            category = await interaction.guild.create_category(msg.content)
            self.tickets_data['ticket_configs'][channel_id]['categories'][category_id]['category_id'] = category.id
            self.save_tickets()
            
            await self.current_context.send(f"✅ Catégorie Discord mise à jour: {category.name}")
        except asyncio.TimeoutError:
            await self.current_context.send("❌ Temps écoulé, modification annulée.")

    async def handle_category_message_edit(self, interaction: discord.Interaction, channel_id: str, category_id: str):
        """Gère la modification du message de bienvenue d'une catégorie"""
        cat_info = self.ticket_categories[category_id]
        
        embed = discord.Embed(
            title=f"✏️ Modification du Message - {cat_info['name']}",
            description="Choisissez une option :",
            color=cat_info['color']
        )
        
        view = discord.ui.View(timeout=60)
        view.add_item(discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Message par Défaut",
            emoji="✅",
            custom_id=f"use_default_message:{channel_id}:{category_id}"
        ))
        view.add_item(discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Message Personnalisé",
            emoji="✏️",
            custom_id=f"custom_message:{channel_id}:{category_id}"
        ))

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        asyncio.create_task(self.delete_after(interaction))

    @commands.command(name="ticket_logs")
    @commands.has_permissions(administrator=True)
    async def ticket_logs(self, ctx, channel: discord.TextChannel = None):
        """Configure ou affiche le salon des logs des tickets"""
        if channel is None:
            # Afficher le salon actuel
            current_logs = self.tickets_data.get('log_channel_id')
            if current_logs:
                current_channel = ctx.guild.get_channel(current_logs)
                if current_channel:
                    embed = discord.Embed(
                        title="📋 Configuration des Logs",
                        description=f"Le salon des logs actuel est : {current_channel.mention}",
                        color=discord.Color.blue()
                    )
                    view = discord.ui.View(timeout=60)
                    view.add_item(discord.ui.Button(
                        style=discord.ButtonStyle.danger,
                        label="Modifier",
                        emoji="✏️",
                        custom_id="edit_logs"
                    ))
                    await ctx.send(embed=embed, view=view)
                else:
                    await ctx.send("❌ Le salon des logs n'est pas configuré ou n'existe plus.")
            else:
                await ctx.send("❌ Aucun salon des logs n'est configuré.\nUtilisez `?ticket_logs #salon` pour en définir un.")
            return

        # Configurer le nouveau salon
        self.tickets_data['log_channel_id'] = channel.id
        self.save_tickets()

        embed = discord.Embed(
            title="✅ Configuration des Logs",
            description=f"Le salon des logs a été défini sur : {channel.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.data or not interaction.data.get('custom_id'):
            return

        custom_id = interaction.data['custom_id']

        # Ajouter le cas pour l'édition des logs
        if custom_id == "edit_logs":
            await interaction.response.send_message(
                "📝 Mentionnez le nouveau salon des logs.",
                ephemeral=True
            )
            try:
                msg = await self.bot.wait_for(
                    'message',
                    timeout=60.0,
                    check=lambda m: m.author == interaction.user and m.channel == interaction.channel and len(m.channel_mentions) > 0
                )
                new_channel = msg.channel_mentions[0]
                self.tickets_data['log_channel_id'] = new_channel.id
                self.save_tickets()
                
                embed = discord.Embed(
                    title="✅ Configuration des Logs",
                    description=f"Le salon des logs a été mis à jour : {new_channel.mention}",
                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=embed)
            except asyncio.TimeoutError:
                await interaction.followup.send("❌ Temps écoulé, aucune modification n'a été effectuée.", ephemeral=True)
            return

        # Ajouter les nouveaux cas pour la gestion des catégories
        if custom_id.startswith('edit_category:'):
            _, channel_id, category_id = custom_id.split(':')
            await self.handle_category_edit(interaction, channel_id, category_id)
        elif custom_id.startswith('edit_cat_discord:'):
            _, channel_id, category_id = custom_id.split(':')
            await self.handle_category_discord_edit(interaction, channel_id, category_id)
        elif custom_id.startswith('edit_cat_message:'):
            _, channel_id, category_id = custom_id.split(':')
            await self.handle_category_message_edit(interaction, channel_id, category_id)
        elif custom_id.startswith('use_default_message:'):
            _, channel_id, category_id = custom_id.split(':')
            cat_info = self.ticket_categories[category_id]
            self.tickets_data['ticket_configs'][channel_id]['categories'][category_id]['welcome_message'] = cat_info['default_message']
            self.save_tickets()
            await interaction.response.send_message("✅ Message par défaut restauré!", ephemeral=True)
            asyncio.create_task(self.delete_after(interaction))
        elif custom_id.startswith('custom_message:'):
            _, channel_id, category_id = custom_id.split(':')
            await interaction.response.send_message("📝 Écrivez votre message personnalisé. Utilisez {user} pour mentionner l'utilisateur.", ephemeral=True)
            asyncio.create_task(self.delete_after(interaction))
            
            try:
                msg = await self.bot.wait_for(
                    'message',
                    timeout=120.0,
                    check=lambda m: m.author == interaction.user and m.channel == interaction.channel
                )
                
                self.tickets_data['ticket_configs'][channel_id]['categories'][category_id]['welcome_message'] = msg.content
                self.save_tickets()
                await interaction.followup.send("✅ Message personnalisé enregistré!", ephemeral=True)
                asyncio.create_task(self.delete_after(interaction.followup))
            except asyncio.TimeoutError:
                await interaction.followup.send("❌ Temps écoulé, modification annulée.", ephemeral=True)
                asyncio.create_task(self.delete_after(interaction.followup))
        elif custom_id.startswith('create_ticket:'):
            # Extraire les IDs du custom_id
            _, channel_id, category_id = custom_id.split(':')
            channel_id = int(channel_id)
            
            # Vérifier si la configuration existe toujours
            if str(channel_id) not in self.tickets_data['ticket_configs']:
                await interaction.response.send_message("❌ La configuration de tickets n'existe plus.", ephemeral=True)
                asyncio.create_task(self.delete_after(interaction))
                return

            # Vérifier si l'utilisateur a déjà un ticket ouvert
            if str(interaction.user.id) in self.tickets_data['active_tickets']:
                existing_ticket = self.tickets_data['active_tickets'][str(interaction.user.id)]
                channel = interaction.guild.get_channel(existing_ticket['channel_id'])
                if channel:
                    await interaction.response.send_message(
                        f"❌ Vous avez déjà un ticket ouvert : {channel.mention}",
                        ephemeral=True
                    )
                    asyncio.create_task(self.delete_after(interaction))
                    return

            # Récupérer la configuration du canal
            config = self.tickets_data['ticket_configs'][str(channel_id)]
            
            # Récupérer les informations de la catégorie depuis self.ticket_categories
            category_info = self.ticket_categories.get(category_id)
            if not category_info:
                await interaction.response.send_message("❌ Cette catégorie n'existe plus.", ephemeral=True)
                return

            # Créer le canal du ticket
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            }

            # Ajouter les permissions pour le rôle support
            if config['support_role_id']:
                support_role = interaction.guild.get_role(config['support_role_id'])
                if support_role:
                    overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

            # Créer le canal dans la catégorie appropriée
            discord_category = None
            if 'categories' in config and category_id in config['categories']:
                category_config = config['categories'][category_id]
                if 'category_id' in category_config:
                    discord_category = interaction.guild.get_channel(category_config['category_id'])

            # Créer le canal
            ticket_channel = await interaction.guild.create_text_channel(
                name=f"ticket-{interaction.user.name}",
                category=discord_category,
                overwrites=overwrites,
                reason=f"Ticket créé par {interaction.user}"
            )

            # Créer le message de bienvenue avec les informations de self.ticket_categories
            embed = discord.Embed(
                title=f"{category_info['emoji']} Nouveau Ticket - {category_info['name']}",
                description=category_info['default_message'].format(user=interaction.user.mention),
                color=category_info['color']
            )
            embed.set_footer(text=f"ID du ticket: {ticket_channel.id}")

            view = discord.ui.View(timeout=None)
            close_button = discord.ui.Button(
                style=discord.ButtonStyle.danger,
                label="Fermer le ticket",
                emoji="🔒",
                custom_id=f"close_ticket:{ticket_channel.id}"
            )
            view.add_item(close_button)

            welcome_msg = await ticket_channel.send(
                content=f"{interaction.user.mention} {support_role.mention if support_role else ''}",
                embed=embed,
                view=view
            )

            # Sauvegarder les informations du ticket
            self.tickets_data['active_tickets'][str(interaction.user.id)] = {
                'channel_id': ticket_channel.id,
                'category_id': category_id,
                'welcome_message_id': welcome_msg.id,
                'created_at': datetime.utcnow().isoformat()
            }
            self.save_tickets()

            await interaction.response.send_message(
                f"✅ Votre ticket a été créé : {ticket_channel.mention}",
                ephemeral=True
            )
            asyncio.create_task(self.delete_after(interaction))

        elif custom_id.startswith('close_ticket:'):
            # Extraire l'ID du canal
            _, ticket_channel_id = custom_id.split(':')
            ticket_channel_id = int(ticket_channel_id)
            
            # Vérifier si le canal existe
            ticket_channel = interaction.guild.get_channel(ticket_channel_id)
            if not ticket_channel:
                await interaction.response.send_message("❌ Ce ticket n'existe plus.", ephemeral=True)
                return

            # Vérifier les permissions
            member_permissions = ticket_channel.permissions_for(interaction.user)
            if not (member_permissions.manage_channels or interaction.user.id == int(next(
                (user_id for user_id, ticket in self.tickets_data['active_tickets'].items() 
                if ticket['channel_id'] == ticket_channel_id), 0
            ))):
                await interaction.response.send_message("❌ Vous n'avez pas la permission de fermer ce ticket.", ephemeral=True)
                return

            # Créer le message de confirmation
            embed = discord.Embed(
                title="🔒 Fermeture du Ticket",
                description="Êtes-vous sûr de vouloir fermer ce ticket ?\nUne transcription sera générée avant la fermeture.",
                color=discord.Color.orange()
            )

            view = discord.ui.View(timeout=None)
            confirm_button = discord.ui.Button(
                style=discord.ButtonStyle.danger,
                label="Confirmer",
                emoji="✅",
                custom_id=f"confirm_close:{ticket_channel_id}"
            )
            cancel_button = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Annuler",
                emoji="❌",
                custom_id=f"cancel_close:{ticket_channel_id}"
            )
            view.add_item(confirm_button)
            view.add_item(cancel_button)

            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            asyncio.create_task(self.delete_after(interaction))

        elif custom_id.startswith('confirm_close:'):
            _, ticket_channel_id = custom_id.split(':')
            ticket_channel_id = int(ticket_channel_id)
            
            # Vérifier si le canal existe
            ticket_channel = interaction.guild.get_channel(ticket_channel_id)
            if not ticket_channel:
                await interaction.response.send_message("❌ Ce ticket n'existe plus.", ephemeral=True)
                return

            # Générer la transcription
            transcript = []
            async for message in ticket_channel.history(limit=None, oldest_first=True):
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                content = message.content or ""
                for embed in message.embeds:
                    content += f"\n[Embed: {embed.title}]"
                for attachment in message.attachments:
                    content += f"\n[Pièce jointe: {attachment.filename}]"
                transcript.append(f"[{timestamp}] {message.author}: {content}")

            # Créer le fichier de transcription
            transcript_content = "\n".join(transcript)
            transcript_file = discord.File(
                io.StringIO(transcript_content),
                filename=f"transcript-{ticket_channel.name}.txt"
            )

            # Trouver l'utilisateur qui a créé le ticket
            creator_id = next(
                (user_id for user_id, ticket in self.tickets_data['active_tickets'].items() 
                if ticket['channel_id'] == ticket_channel_id),
                None
            )

            # Envoyer la transcription en MP
            if creator_id:
                creator = interaction.guild.get_member(int(creator_id))
                if creator:
                    try:
                        embed_mp = discord.Embed(
                            title="📝 Transcription du Ticket",
                            description=f"Voici la transcription de votre ticket dans {interaction.guild.name}.",
                            color=discord.Color.blue()
                        )
                        await creator.send(embed=embed_mp, file=discord.File(
                            io.StringIO(transcript_content),
                            filename=f"transcript-{ticket_channel.name}.txt"
                        ))
                    except discord.Forbidden:
                        pass  # L'utilisateur a peut-être bloqué les MPs

            # Envoyer la transcription dans le salon de logs
            if self.tickets_data.get('log_channel_id'):
                log_channel = interaction.guild.get_channel(self.tickets_data['log_channel_id'])
                if log_channel:
                    embed_log = discord.Embed(
                        title="📝 Ticket Fermé",
                        description=f"**Ticket:** {ticket_channel.name}\n"
                                  f"**Créé par:** {creator.mention if creator else 'Inconnu'}\n"
                                  f"**Fermé par:** {interaction.user.mention}",
                        color=discord.Color.orange(),
                        timestamp=datetime.utcnow()
                    )
                    await log_channel.send(
                        embed=embed_log,
                        file=discord.File(
                            io.StringIO(transcript_content),
                            filename=f"transcript-{ticket_channel.name}.txt"
                        )
                    )

            # Supprimer le ticket des données
            if creator_id:
                del self.tickets_data['active_tickets'][creator_id]
                self.save_tickets()

            # Supprimer le canal
            await ticket_channel.delete(reason="Ticket fermé")
            await interaction.response.send_message("✅ Le ticket a été fermé et la transcription a été envoyée.", ephemeral=True)
            asyncio.create_task(self.delete_after(interaction))

        elif custom_id.startswith('cancel_close:'):
            await interaction.response.send_message("❌ Fermeture du ticket annulée.", ephemeral=True)
            asyncio.create_task(self.delete_after(interaction))
        elif custom_id.startswith('confirm_delete:'):
            _, channel_id = custom_id.split(':')
            await self.handle_confirm_delete(interaction, channel_id)
            asyncio.create_task(self.delete_after(interaction))
        elif custom_id.startswith('cancel_delete:'):
            await interaction.response.send_message("❌ Suppression annulée.", ephemeral=True)
            asyncio.create_task(self.delete_after(interaction))
        elif custom_id.startswith('edit_role:'):
            _, channel_id = custom_id.split(':')
            await self.handle_role_edit(interaction, channel_id)

    @commands.command(name="set_priority")
    @commands.has_permissions(administrator=True)
    async def set_priority(self, ctx, priority: str = None):
        """Définit la priorité d'un ticket"""
        # Vérifier si le canal est un ticket
        ticket_info = None
        ticket_owner_id = None
        
        # Chercher le ticket dans les tickets actifs
        for user_id, ticket in self.tickets_data['active_tickets'].items():
            if ticket['channel_id'] == ctx.channel.id:
                ticket_info = ticket
                ticket_owner_id = user_id
                break

        if not ticket_info:
            await ctx.send("❌ Ce salon n'est pas un ticket!")
            return

        if priority is None or priority.lower() not in self.priorities:
            priorities_list = ", ".join(self.priorities.keys())
            await ctx.send(f"❌ Veuillez spécifier une priorité valide : {priorities_list}")
            return

        priority = priority.lower()
        
        # Mettre à jour la priorité dans les données du ticket
        ticket_info['priority'] = priority
        
        # Mettre à jour les statistiques
        if 'tickets_by_priority' not in self.tickets_data['ticket_stats']:
            self.tickets_data['ticket_stats']['tickets_by_priority'] = {
                "basse": 0,
                "moyenne": 0,
                "haute": 0,
                "urgente": 0
            }
        self.tickets_data['ticket_stats']['tickets_by_priority'][priority] += 1
        self.save_tickets()

        # Mettre à jour le nom du salon avec l'emoji de priorité
        priority_emoji = self.priorities[priority]['emoji']
        current_name = ctx.channel.name
        
        # Liste de tous les emojis de priorité
        priority_emojis = [p['emoji'] for p in self.priorities.values()]
        
        # Vérifier si le nom actuel commence par un emoji de priorité
        has_priority_emoji = any(current_name.startswith(emoji) for emoji in priority_emojis)
        
        if has_priority_emoji:
            # Remplacer l'ancien emoji par le nouveau
            for emoji in priority_emojis:
                if current_name.startswith(emoji):
                    new_name = current_name.replace(emoji, priority_emoji, 1)
                    break
        else:
            # Ajouter l'emoji au début du nom
            new_name = f"{priority_emoji}{current_name}"
            
        await ctx.channel.edit(name=new_name)

        embed = discord.Embed(
            title="🎯 Priorité Mise à Jour",
            description=f"La priorité du ticket a été définie sur : **{priority}** {self.priorities[priority]['emoji']}",
            color=self.priorities[priority]['color']
        )
        await ctx.send(embed=embed)

    @commands.command(name="tickets_priority")
    @commands.has_permissions(administrator=True)
    async def tickets_priority(self, ctx):
        """Affiche la liste des tickets par priorité"""
        active_tickets = {}
        
        # Organiser les tickets par priorité
        for ticket_id, ticket_data in self.tickets_data['active_tickets'].items():
            priority = ticket_data.get('priority', 'non définie')
            if priority not in active_tickets:
                active_tickets[priority] = []
            channel = ctx.guild.get_channel(int(ticket_id))
            if channel:
                active_tickets[priority].append(channel)

        embed = discord.Embed(
            title="📊 Liste des Tickets par Priorité",
            color=discord.Color.blue()
        )

        # Ajouter les tickets pour chaque priorité
        for priority in ['urgente', 'haute', 'moyenne', 'basse', 'non définie']:
            tickets = active_tickets.get(priority, [])
            if tickets:
                emoji = self.priorities.get(priority, {}).get('emoji', '⚪')
                ticket_list = "\n".join([f"• {ticket.mention}" for ticket in tickets])
                embed.add_field(
                    name=f"{emoji} Priorité {priority.capitalize()} ({len(tickets)})",
                    value=ticket_list,
                    inline=False
                )

        # Ajouter les statistiques
        stats = self.tickets_data['ticket_stats']['tickets_by_priority']
        stats_text = "\n".join([
            f"{self.priorities[p]['emoji']} **{p.capitalize()}:** {stats[p]} tickets"
            for p in self.priorities
        ])
        embed.add_field(
            name="📈 Statistiques Globales",
            value=stats_text,
            inline=False
        )

        await ctx.send(embed=embed)

    async def handle_confirm_delete(self, interaction: discord.Interaction, channel_id: str):
        """Gère la confirmation de suppression d'une configuration"""
        # Implémentation de la gestion de la suppression d'une configuration
        pass

async def setup(bot):
    await bot.add_cog(TicketsCog(bot)) 