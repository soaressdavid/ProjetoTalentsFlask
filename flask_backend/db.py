#importa o ORM do SQLAlchemy, que facilita interagir com o banco de dados
from flask_sqlalchemy import SQLAlchemy
#importa o CORS para permitir que seu frontend acesse a API
from flask_cors import CORS

#cria uma instância global do SQLAlchemy que será associada ao app Flask depois
db = SQLAlchemy()

def configure_cors(app, allowed_origins: list[str]) -> None:
    """
    Configura o CORS para o app Flask
    app: instaância do flask
    allowed_origins: lista de origens permitidas (ex.:http//localhost:3000)
    o dicionário resources limita o CORS às rotas que começam com /api/*
    """
    CORS(app, resources={r"/api/*": {"origins": allowed_origins or "*"}})