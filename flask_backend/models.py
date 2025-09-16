#importa a instância do banco e utilitários de hash de senha
from flask_backend.db import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """
    Modelo de Usuário.
    Representa a tabela 'users' no banco de dados.
    Armazena email único e o hash da senha (nunca a senha em texto puro).
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password: str) -> None:
        """
        recebe a senha em texto e guarda apenas o hash seguro
        o generate_password_hash usa um algoritmo forte (ex.:PBKDF2)
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """
        compara a senha informada com o hash salvo
        retorna True se a senha estiver correta; False caso contrário
        """
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self) -> str:
        """
        representação útil para logs e debug
        """
        return f"<User {self.email}"

