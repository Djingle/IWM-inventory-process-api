# IWMI_api webserver
## Tutoriel
- https://www.mongodb.com/languages/python/pymongo-tutorial

## Installation
```pip install -r requirements.txt```

## Lancement
```python3 -m uvicorn webserver:IWMI_api --reload```
- l'option `--reload` est à des fins de développement seulement

## Usage/Test
### Simuler une requête venant du drone, vers le serveur (requête dûe à la lecture d'un code barre)
*Note : l'adresse du serveur doit être réglée au besoin*
```python3 xml_drone_emitter_test.py```

## Notes
- En général le serveur est accessible à l'adresse locale http://127.0.0.1:8000/.
- Dans `.env` il y a les paramètres de connexion à MongoDB
- Les fichiers requirements.txt, runtime.txt et Procfile servent pour l'hébergement de l'API sur Herokuapp
- L'API est accessible en ligne via https://iwmi.herokuapp.com/ (*par contre pour la mettre à jour avec la version de gitlab il faut passer par Titouan*)