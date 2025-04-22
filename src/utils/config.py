import json
import os
from typing import Dict, Any

DEFAULT_CONFIG = {
    "banned_words": [
        "cheat", "cheats", "hack", "hacks",
        "internal", "external", "ddos",
        "denial of service", "spam", "raid"
    ],
    "banned_extensions": [
        ".dll", ".exe", ".bat", ".cmd",
        ".msi", ".vbs", ".js", ".jar"
    ],
    "log_channel_id": None,
    "admin_role_id": None,  # ID du rôle admin
    "owner_id": None,       # ID du propriétaire du bot
    "max_warnings": 3,
    "warning_duration": 24,  # en heures
    "auto_timeout": True,
    "timeout_duration": 3600,  # en secondes
    "status": "Surveille informaclique",
    "welcome_channel_id": None,  # ID du canal de bienvenue
    "welcome_message": "Bienvenue {member.mention} sur le serveur ! 🎉\nNous sommes maintenant {member_count} membres !",
    "goodbye_message": "Au revoir {member.name} ! 😢\nNous sommes maintenant {member_count} membres.",
    "auto_reactions": {},  # Format: {"channel_id": ["emoji1", "emoji2", ...]}
    "auto_reaction_chance": 0.3  # Probabilité de réaction (30%)
}

def load_config() -> Dict[str, Any]:
    """Charge la configuration depuis le fichier config.json"""
    config_path = "data/config.json"
    
    # Création du dossier data s'il n'existe pas
    os.makedirs("data", exist_ok=True)
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            
        # Mise à jour de la configuration avec les nouvelles clés si nécessaire
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
                
        return config
    except FileNotFoundError:
        # Si le fichier n'existe pas, on crée une configuration par défaut
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]) -> None:
    """Sauvegarde la configuration dans le fichier config.json"""
    config_path = "data/config.json"
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False) 