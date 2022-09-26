# IWMI_api webserver
## Tutoriel
- https://www.mongodb.com/languages/python/pymongo-tutorial

## Installation
```python -m pip install 'fastapi[all]' 'pymongo[srv]' python-dotenv```

## Lancement
```python3 -m uvicorn webserver:IWMI_api```

## Notes
- En général le serveur est accessible à l'adresse locale http://127.0.0.1:8000/.
- Dans `.env` il y a les paramètres de connexion à MongoDB