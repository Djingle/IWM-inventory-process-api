# IWMI_api webserver
## Installation
```python -m pip install 'fastapi[all]' 'pymongo[srv]' python-dotenv```

## Lancement
```python3 -m uvicorn webserver2:IWMI_api```

## Notes
- En général le serveur est accessible à l'adresse locale http://127.0.0.1:8000/.
- Dans `.env` il y a les paramètres de connexion à MongoDB