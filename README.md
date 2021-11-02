# Auto Modérateur Bot Discord

Un bot pour modéré facilement vos serveurs discord !

[![forthebadge](https://forthebadge.com/images/badges/open-source.svg)](http://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](http://forthebadge.com)

## Pré requis :

Python 3.X

## Installation

1. Crée votre application Discord juste ici : https://discordapp.com/developers/applications/me

2. Ensuite crée un bot dans l'onglet "Bot"

3. Récupéré le token de votre Bot et l'inséré tout en bas du fichier modo.py

## Configuration des mots bannis :

Rendez-vous à la ligne 11, dans word list. 

Ici vous pouvez ajouté, une multitude de mots que vous en souhaité pas que les gens disent sur votre serveur !!

## Configuration des fichiers bannis : 

Entre la ligne 24 et 31, c'est ici que vous trouverez le code, pour empêché les utilisateurs d'upload des fichiers spécifiques que vous aurez configuré. 

De base, les .dll et .exe sont interdits. Si vous souhaité vous pouvez en ajouté d'autre ou en supprimé. 

Si vous souhaité par exemple interdire l'upload de .pdf, allé a la ligne 30 et copié les 2 lignes : 

```
elif attachment.filename.endswith('.exe'):
                    await message.delete()
                    await message.channel.send("Les upload de .exe ne sont pas autorisé ici!")
```

Une fois cela copié modifié les valeurs donc pour notre exemple en pdf cela nous donne : 

```
elif attachment.filename.endswith('.pdf'):
                    await message.delete()
                    await message.channel.send("Les upload de .pdf ne sont pas autorisé ici!")
```

Et voilà. 

Bon courage, si vous avez une requète, besoin d'aide ou tout autre question n'hésité pas !

