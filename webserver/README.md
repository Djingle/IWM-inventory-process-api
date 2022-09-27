# IWMI_api webserver
## Tutoriel
- https://www.mongodb.com/languages/python/pymongo-tutorial

## Installation
```python3 -m pip install 'fastapi[all]' 'pymongo[srv]' python-dotenv xmltodict```

## Lancement
```python3 -m uvicorn webserver:IWMI_api```

## Usage/Test
### Simuler une requête venant du drone, vers le serveur (requête dûe à la lecture d'un code barre)
*Note : l'adresse du serveur doit être réglée au besoin*
```python3 xml_drone_emitter_test.py```

## Notes
- En général le serveur est accessible à l'adresse locale http://127.0.0.1:8000/.
- Dans `.env` il y a les paramètres de connexion à MongoDB