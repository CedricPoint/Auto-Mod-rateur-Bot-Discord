import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
from cogs.moderation import ModerationCog
from cogs.config import ConfigCog
from cogs.help import HelpCog
from utils.config import load_config, save_config

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('discord')

# Chargement des variables d'environnement
load_dotenv()

class AutoModBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='?',
            intents=intents,
            help_command=None
        )
        
        self.config = load_config()
        self.logger = logger

    async def setup_hook(self):
        # Chargement des cogs
        await self.add_cog(ModerationCog(self))
        await self.add_cog(ConfigCog(self))
        await self.add_cog(HelpCog(self))
        
        # Synchronisation des commandes slash
        try:
            synced = await self.tree.sync()
            self.logger.info(f"Commandes slash synchronisées: {len(synced)}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la synchronisation des commandes slash: {e}")

    async def on_ready(self):
        self.logger.info(f'Connecté en tant que {self.user.name} ({self.user.id})')
        self.logger.info('------')
        
        # Définition du statut
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=self.config["status"]
            )
        )

    def is_admin(self, user: discord.Member) -> bool:
        """Vérifie si un utilisateur est admin"""
        if self.config["admin_role_id"]:
            return any(role.id == self.config["admin_role_id"] for role in user.roles)
        return user.guild_permissions.administrator

    def is_owner(self, user: discord.User) -> bool:
        """Vérifie si un utilisateur est le propriétaire du bot"""
        return user.id == self.config["owner_id"]

def main():
    bot = AutoModBot()
    bot.run(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    main() 