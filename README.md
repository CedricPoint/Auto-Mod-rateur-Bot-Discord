# Auto Mod Bot

Un bot Discord puissant pour la modération automatique et la gestion de tickets, développé pour Informaclique.

## 🌟 Fonctionnalités

### 🎫 Système de Tickets
- **Configuration Multiple**
  - Plusieurs points de création de tickets dans différents salons
  - 4 catégories prédéfinies : Support, Bug, Commande, Autre
  - Messages de bienvenue personnalisables par catégorie
  - Système de priorité avec emojis colorés

- **Gestion des Tickets**
  - Création de tickets avec boutons interactifs
  - Système de priorité (basse 🟢, moyenne 🟡, haute 🟠, urgente 🔴)
  - Transcription automatique à la fermeture
  - Logs détaillés des actions
  - Statistiques par catégorie et priorité

### 🛡️ Modération
- **Gestion des Messages**
  - Suppression automatique des mots interdits
  - Filtrage des fichiers par extension
  - Commande de nettoyage rapide
  - Messages de modération avec embeds

- **Système d'Avertissements**
  - Avertissements automatiques et manuels
  - Timeout automatique après X avertissements
  - Gestion des avertissements par membre
  - Historique des avertissements

### 💫 Messages et Réactions
- **Messages Automatiques**
  - Messages de bienvenue personnalisables
  - Messages d'au revoir
  - Compteur de membres précis (sans bots)

- **Réactions Automatiques**
  - Configuration par salon
  - Ajout de réactions aux anciens messages
  - Probabilité de réaction configurable

## 📋 Commandes

### Système de Tickets
```
?ticket_setup #salon    : Configure le système de tickets
?ticket_list           : Liste les configurations actives
?ticket_edit #salon    : Modifie une configuration existante
?ticket_delete #salon  : Supprime une configuration
?ticket_logs [#salon]  : Gère le salon des logs des tickets
?close                 : Ferme le ticket actuel
?set_priority <niveau> : Définit la priorité d'un ticket
?tickets_priority      : Liste les tickets par priorité
```

### Modération
```
?clear <nombre>              : Supprime des messages
?warn @membre <raison>       : Avertit un membre
?warnings @membre            : Affiche les avertissements
?clearwarns @membre         : Supprime les avertissements
?add_banned_word <mot>       : Ajoute un mot interdit
?remove_banned_word <mot>    : Retire un mot interdit
?list_banned_words          : Liste les mots interdits
?list_banned_files          : Liste les extensions interdites
```

### Configuration
```
?set_log_channel #salon      : Définit le salon des logs
?set_welcome_channel #salon  : Définit le salon de bienvenue
?set_welcome_message <texte> : Configure le message de bienvenue
?set_goodbye_message <texte> : Configure le message d'au revoir
?set_owner @utilisateur     : Définit le propriétaire
?set_admin_role @role       : Définit le rôle administrateur
?set_status <texte>         : Change le statut du bot
```

### Réactions
```
?add_auto_reaction #salon emoji    : Configure une réaction automatique
?remove_auto_reaction #salon emoji : Retire une réaction automatique
?list_auto_reactions              : Liste les réactions configurées
?react_history #salon <nombre>    : Ajoute les réactions aux anciens messages
```

## ⚙️ Configuration

### Variables d'Environnement
Créez un fichier `.env` basé sur `.env.example` :
```env
DISCORD_TOKEN=votre_token_ici
```

### Installation
1. Clonez le repository
2. Installez les dépendances : `pip install -r requirements.txt`
3. Configurez le fichier `.env`
4. Lancez le bot : `PYTHONPATH=$PYTHONPATH:. python src/bot.py`

### Installation Persistante (Linux)
Pour une installation persistante avec systemd :

1. Créez un fichier service :
```bash
sudo nano /etc/systemd/system/automodbot.service
```

2. Ajoutez la configuration :
```ini
[Unit]
Description=Auto Mod Bot Discord
After=network.target

[Service]
Type=simple
User=votre_utilisateur
WorkingDirectory=/chemin/vers/le/bot
Environment=PYTHONPATH=/chemin/vers/le/bot
ExecStart=/bin/sh -c 'PYTHONPATH=$PYTHONPATH:/chemin/vers/le/bot /chemin/vers/venv/bin/python src/bot.py'
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

3. Activez et démarrez le service :
```bash
sudo systemctl enable automodbot
sudo systemctl start automodbot
```

4. Commandes utiles :
```bash
sudo systemctl status automodbot  # Voir l'état
sudo systemctl stop automodbot    # Arrêter
sudo systemctl restart automodbot # Redémarrer
journalctl -u automodbot -f      # Voir les logs
```

## 🔒 Sécurité
- Les tokens et configurations sensibles sont stockés dans le fichier `.env`
- Les permissions sont vérifiées pour chaque commande
- Les logs détaillés de toutes les actions sont disponibles
- Système de backup automatique des configurations

## 🤝 Contribution
Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push sur la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence
Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👤 Auteur
**CedricPoint**
- GitHub: [@CedricPoint](https://github.com/CedricPoint)

## ⭐ Support
Si vous aimez ce projet, n'hésitez pas à lui donner une étoile sur GitHub !

