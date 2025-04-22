import discord
from discord.ext import commands
import asyncio

class HelpView(discord.ui.View):
    def __init__(self, help_embeds):
        super().__init__(timeout=180)
        self.help_embeds = help_embeds
        self.current_page = 0

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page - 1) % len(self.help_embeds)
        await interaction.response.edit_message(embed=self.help_embeds[self.current_page], view=self)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page + 1) % len(self.help_embeds)
        await interaction.response.edit_message(embed=self.help_embeds[self.current_page], view=self)

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_help_embeds(self):
        help_embeds = []

        # Page 1: Système de Tickets
        embed_tickets = discord.Embed(
            title="🎫 Système de Tickets",
            description="Commandes pour gérer le système de tickets",
            color=discord.Color.blue()
        )
        embed_tickets.add_field(
            name="Configuration des Tickets",
            value="""
`?ticket_setup #salon` : Configure le système de tickets dans un salon
• Configure les messages de bienvenue pour chaque catégorie
• Définit le rôle support et le salon des logs
• Crée les catégories Discord pour chaque type de ticket

`?ticket_list` : Affiche toutes les configurations de tickets
• Liste les panneaux de tickets actifs
• Montre les statistiques par catégorie
• Affiche les messages configurés

`?ticket_edit #salon` : Modifie une configuration existante
• Permet de modifier chaque catégorie individuellement
• Modification des messages de bienvenue
• Changement du rôle support
• Modification des catégories Discord

`?ticket_delete #salon` : Supprime une configuration
• Supprime les catégories Discord associées
• Retire le panneau de tickets

`?ticket_logs [#salon]` : Gère le salon des logs des tickets
• Sans argument : affiche le salon actuel
• Avec #salon : définit un nouveau salon
• Bouton pour modifier rapidement
""",
            inline=False
        )
        embed_tickets.add_field(
            name="Gestion des Tickets",
            value="""
`?close` : Ferme le ticket actuel
• Crée une transcription complète
• Envoie une copie au créateur du ticket
• Envoie les logs dans le salon configuré
• Supprime le salon du ticket

`?set_priority <priorité>` : Définit la priorité d'un ticket
• Options : basse, moyenne, haute, urgente
• Change l'emoji du ticket
• Met à jour les statistiques
• Modifie la couleur des messages

`?tickets_priority` : Liste les tickets par priorité
• Affiche les tickets actifs par niveau de priorité
• Montre les statistiques globales
• Permet un suivi des tickets urgents
""",
            inline=False
        )
        help_embeds.append(embed_tickets)

        # Page 2: Modération
        embed_moderation = discord.Embed(
            title="🛡️ Commandes de Modération",
            description="Commandes pour la modération du serveur",
            color=discord.Color.red()
        )
        embed_moderation.add_field(
            name="Gestion des Messages",
            value="""
`?clear <nombre>` : Supprime un nombre spécifié de messages
`?add_banned_word <mot>` : Ajoute un mot à la liste des mots interdits
`?remove_banned_word <mot>` : Retire un mot de la liste des mots interdits
`?list_banned_words` : Affiche la liste des mots interdits
`?list_banned_files` : Affiche la liste des extensions de fichiers interdites
""",
            inline=False
        )
        embed_moderation.add_field(
            name="Gestion des Avertissements",
            value="""
`?warn <@membre> <raison>` : Donne un avertissement à un membre
`?warnings <@membre>` : Affiche les avertissements d'un membre
`?clearwarns <@membre>` : Supprime tous les avertissements d'un membre
""",
            inline=False
        )
        help_embeds.append(embed_moderation)

        # Page 3: Configuration
        embed_config = discord.Embed(
            title="⚙️ Configuration",
            description="Commandes de configuration du bot",
            color=discord.Color.green()
        )
        embed_config.add_field(
            name="Configuration Générale",
            value="""
`?set_log_channel #salon` : Définit le salon des logs
`?set_welcome_channel #salon` : Définit le salon de bienvenue
`?set_welcome_message <message>` : Configure le message de bienvenue
`?set_goodbye_message <message>` : Configure le message d'au revoir
`?show_welcome_config` : Affiche la configuration actuelle
""",
            inline=False
        )
        embed_config.add_field(
            name="Configuration des Rôles",
            value="""
`?set_owner @utilisateur` : Définit le propriétaire du bot
`?set_admin_role @role` : Définit le rôle administrateur
`?set_mod_role @role` : Définit le rôle modérateur
`?set_status <texte>` : Change le statut du bot
""",
            inline=False
        )
        help_embeds.append(embed_config)

        # Page 4: Messages et Réactions
        embed_reactions = discord.Embed(
            title="💫 Messages et Réactions",
            description="Configuration des messages et réactions automatiques",
            color=discord.Color.purple()
        )
        embed_reactions.add_field(
            name="Réactions Automatiques",
            value="""
`?add_auto_reaction #salon emoji` : Ajoute une réaction automatique
`?remove_auto_reaction #salon emoji` : Retire une réaction automatique
`?list_auto_reactions` : Affiche la liste des réactions automatiques
`?react_history #salon <nombre>` : Ajoute les réactions aux anciens messages
""",
            inline=False
        )
        embed_reactions.add_field(
            name="Paramètres des Réactions",
            value="""
`?set_reaction_chance <pourcentage>` : Définit la probabilité de réaction
`?toggle_reactions #salon` : Active/désactive les réactions dans un salon
""",
            inline=False
        )
        help_embeds.append(embed_reactions)

        # Page 5: Statistiques et Info
        embed_stats = discord.Embed(
            title="📊 Statistiques et Informations",
            description="Commandes pour voir les statistiques et informations",
            color=discord.Color.gold()
        )
        embed_stats.add_field(
            name="Statistiques",
            value="""
`?stats` : Affiche les statistiques du serveur
• Nombre de membres
• Nombre de tickets créés
• Statistiques de modération
• Statistiques des tickets par priorité
• Statistiques des tickets par catégorie

`?info` : Affiche les informations du bot
• Version du bot
• Temps de fonctionnement
• Latence
• Nombre de commandes disponibles

`?setup_stats` : Configure les compteurs de statistiques
• Membres totaux
• Membres en ligne
• Nombre de salons
• Nombre de tickets actifs
""",
            inline=False
        )
        help_embeds.append(embed_stats)

        # Ajouter le numéro de page à chaque embed
        for i, embed in enumerate(help_embeds):
            embed.set_footer(text=f"Page {i+1}/{len(help_embeds)}")

        return help_embeds

    @commands.command(name="help")
    async def help(self, ctx):
        """Affiche l'aide du bot"""
        help_embeds = self.create_help_embeds()
        view = HelpView(help_embeds)
        await ctx.send(embed=help_embeds[0], view=view)

async def setup(bot):
    await bot.add_cog(HelpCog(bot)) 