import discord
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx):
        """Affiche la liste des commandes disponibles"""
        embed = discord.Embed(
            title="📚 Commandes Disponibles",
            description="Voici la liste des commandes du bot :",
            color=discord.Color.blue()
        )
        
        # Commandes de modération
        embed.add_field(
            name="🔨 Commandes de Modération",
            value="""`?warn @membre raison` - Donner un avertissement
`?warnings @membre` - Voir les avertissements
`?clear nombre` - Supprimer des messages""",
            inline=False
        )
        
        # Commandes de configuration
        embed.add_field(
            name="⚙️ Commandes de Configuration",
            value="""`?set_owner @utilisateur` - Définir le propriétaire
`?set_admin_role @rôle` - Définir le rôle admin
`?set_status texte` - Changer le statut
`?add_banned_word mot` - Ajouter un mot interdit
`?remove_banned_word mot` - Retirer un mot interdit
`?list_banned_words` - Voir les mots interdits
`?list_banned_files` - Voir les extensions interdites
`?set_log_channel #canal` - Définir le canal de logs
`?add_auto_reaction #canal emoji` - Ajouter une réaction automatique
`?remove_auto_reaction #canal emoji` - Retirer une réaction automatique
`?list_auto_reactions` - Voir les réactions automatiques""",
            inline=False
        )
        
        # Messages de bienvenue
        embed.add_field(
            name="👋 Messages de Bienvenue",
            value="""`?set_welcome_channel #canal` - Définir le salon de bienvenue
`?set_welcome_message texte` - Définir le message de bienvenue
`?set_goodbye_message texte` - Définir le message d'au revoir
`?show_welcome_config` - Voir la configuration actuelle""",
            inline=False
        )
        
        embed.set_footer(text="Auto Mod Bot")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot)) 