# Auto Modérateur Bot Discord

Un bot moderne et puissant pour la modération automatique de votre serveur Discord !

[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](http://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](http://forthebadge.com)

## 🌟 Fonctionnalités

### 🛡️ Modération Automatique
- Détection et suppression des mots interdits
- Blocage des fichiers dangereux (.dll, .exe, .bat, etc.)
- Système d'avertissements avec timeout automatique
- Système de logs détaillé avec embeds
- Messages de suppression automatique après 10 secondes
- Réactions automatiques configurables par salon

### 👋 Messages de Bienvenue
- Messages de bienvenue et d'au revoir personnalisables
- Variables dynamiques pour personnaliser les messages
- Configuration du salon de bienvenue
- Compteur de membres automatique

### ⚙️ Configuration Avancée
- Système de rôles administrateurs
- Configuration du propriétaire du bot
- Gestion des mots interdits
- Gestion des extensions de fichiers interdites
- Configuration des réactions automatiques par salon

## 📚 Commandes

### 🔨 Commandes de Modération
- `?warn @membre raison` - Donner un avertissement
- `?warnings @membre` - Voir les avertissements
- `?clear nombre` - Supprimer des messages

### ⚙️ Commandes de Configuration
- `?set_owner @utilisateur` - Définir le propriétaire
- `?set_admin_role @rôle` - Définir le rôle admin
- `?set_status texte` - Changer le statut
- `?add_banned_word mot` - Ajouter un mot interdit
- `?remove_banned_word mot` - Retirer un mot interdit
- `?list_banned_words` - Voir les mots interdits
- `?list_banned_files` - Voir les extensions interdites
- `?set_log_channel #canal` - Définir le canal de logs

### 🔄 Réactions Automatiques
- `?add_auto_reaction #canal emoji` - Ajouter une réaction automatique
- `?remove_auto_reaction #canal emoji` - Retirer une réaction automatique
- `?list_auto_reactions` - Voir les réactions automatiques

### 👋 Messages de Bienvenue
- `?set_welcome_channel #canal` - Définir le salon de bienvenue
- `?set_welcome_message texte` - Définir le message de bienvenue
- `?set_goodbye_message texte` - Définir le message d'au revoir
- `?show_welcome_config` - Voir la configuration actuelle

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Un bot Discord créé sur le [Portail Développeur Discord](https://discord.com/developers/applications)

### Installation Standard

1. Clonez le dépôt :
```bash
git clone https://github.com/CedricPoint/auto-mod-bot.git
cd auto-mod-bot
```

2. Créez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux
# ou
.\venv\Scripts\activate  # Windows
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurez le bot :
- Copiez `.env.example` en `.env`
- Modifiez `.env` avec votre token Discord :
```env
DISCORD_TOKEN=votre_token_ici
```

5. Lancez le bot :
```bash
PYTHONPATH=$PYTHONPATH:. python src/bot.py
```

### 🐧 Installation sur Linux avec systemd (persistant)

1. Créez un service systemd :
```bash
sudo nano /etc/systemd/system/discord-automod.service
```

2. Ajoutez la configuration suivante :
```ini
[Unit]
Description=Discord Auto Mod Bot
After=network.target

[Service]
Type=simple
User=votre_utilisateur
Group=votre_groupe
WorkingDirectory=/home/informaclique/mododiscord/
Environment="PYTHONPATH=/home/informaclique/mododiscord/"
ExecStart=/bin/sh -c 'PYTHONPATH=$PYTHONPATH:/home/informaclique/mododiscord /home/informaclique/mododiscord/venv/bin/python src/bot.py'
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

3. Activez et démarrez le service :
```bash
sudo systemctl enable discord-automod
sudo systemctl start discord-automod
```

4. Vérifiez le statut :
```bash
sudo systemctl status discord-automod
```

5. Consultez les logs :
```bash
journalctl -u discord-automod -f
```

## 📝 Configuration

Le bot utilise un fichier `config.json` qui est créé automatiquement au premier lancement. Vous pouvez le modifier manuellement ou utiliser les commandes du bot.

### Configuration par défaut :
```json
{
    "banned_words": ["cheat", "hack", "spam", ...],
    "banned_extensions": [".dll", ".exe", ".bat", ...],
    "log_channel_id": null,
    "admin_role_id": null,
    "owner_id": null,
    "max_warnings": 3,
    "warning_duration": 24,
    "auto_timeout": true,
    "timeout_duration": 3600,
    "status": "Surveille informaclique",
    "welcome_channel_id": null,
    "auto_reactions": {}
}
```

## 🔒 Sécurité
- Vérification des permissions pour toutes les commandes
- Protection contre les fichiers dangereux
- Système de logs détaillé
- Timeout automatique après plusieurs avertissements
- Messages de modération en mode ephemeral

## 🤝 Contribution
Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📄 Licence
Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👤 Auteur
**CedricPoint**
- GitHub: [@CedricPoint](https://github.com/CedricPoint)

## ⭐ Support
Si vous aimez ce projet, n'hésitez pas à lui donner une étoile sur GitHub !

