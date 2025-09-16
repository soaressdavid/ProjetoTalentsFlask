#imports padrão de sistema e flask
import os
from flask import Flask, request, jsonify, session, send_from_directory, send_file
#carrega variáveis do arquivo .env para o ambiente
from dotenv import load_dotenv


#importa a instância do banco e configurção do CORS
from flask_backend.db import db, configure_cors
#importa o modelo User para operações de autenticação
from flask_backend.models import User

#carrega variáveis definidas no arquivo .env (na raiz do backend)
load_dotenv()

def create_app() -> Flask:
    """
    fábrica de aplicações: cria e configura uma instância do app Flask
    esse padrão facilita teste e execução em diferentes ambientes
    """
    app = Flask(__name__)
    
    #SECRET_KEY assina cookies de sessão; troque em produção por algo seguro
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key-insegura")
    
    #URL do banco de dados. Por padrão, usa um arquivo SQLite 'app.db'
    # Corrigido para ler a variável DATABASE_URL (como documentado)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    
    #Desativa rastreamento de modificações do SQLAlchemy (economiza recursos)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    #associa a instância global do SQLAlchemy ao app
    db.init_app(app)
    
    #lê origens permitidas do .env e configura CORS para /api/*
    allowed = os.getenv("ALLOWED_ORIGINS", "")
    allowed_origins = [o.strip() for o in allowed.split(",") if o.strip()]
    configure_cors(app, allowed_origins)
    
    #cria automaticamente as tabelas mapeadas pelos modelos (ambiente dev)
    #em produção, prefira usar migrções (Flask-Migrate/Alembic)
    with app.app_context():
        db.create_all()
        
    @app.get('/api/health')
    def health():
        """
        Health-check simples
        Objetivo: verificar rapidamente se o backend está respondendo
        Retorna um JSON: {"status: "ok} com HTTP 200.
        """
        return jsonify({"status": "ok"}), 200
    
    @app.post('/api/register')
    def register():
        """
        endpoint de cadastro de usuário
        espera o JSON com {"email": "...", "password": "..."}
        fluxo:
            valida presença de email e senha
            verifica se já existe usuário com o mesmo email
            cria usuário com senha hasheada e salva no banco de dados
            cretorna 201 created
        """
        
        #Lê JSON do corpo; silent=True evita exceção se não for JSON válido
        data = request.get_json(silent=True) or {}
        #normaliza o email (tira espaços e deia minúsculo)
        email = (data.get("email") or "").strip().lower()
        #obtém a senha enviada
        password = data.get("password") or ""
        
        #validação básica de compos obrigatórios
        if not email or not password:
            return jsonify({"error": "Email e senha são obrigatórios"}), 400
        
        #garante que não existam dois usuários com o mesmo email
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email já cadastrado"}), 409
        
        #cria a instância do usuário e define o hash da senha
        user = User(email=email)
        user.set_password(password)
        
        #inclui no contexto de transação e persiste no banco
        db.session.add(user)
        db.session.commit()
        
        return jsonify({"message": "Usuário criado com sucesso"}), 201
    
    @app.post('/api/login')
    def login():
        """
        endpoint de login
        espera JSON com {"email: "...", "pasword": "..." }
        fluxo:
            busca usuário pelo email
            confere a senha contra o hash
            em caso de sucesso, grava dados mínimos na sessão
            retorna 200 com mensagem e email
        """
        
        data = request.get_json(silent=True) or {}
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        
        user = User.query.filter_by(email=email).first()
        
        #se não encontrar ou a senha estiver incorret, retorna 401
        if not user or not user.check_password(password):
            return jsonify({"error": "Credenciais inválidas"}), 401
        
        session["user_id"] = user.id
        session["user_email"] = user.email
        
        return jsonify({"message": "Login efetuado", "email": user.email}),200
    
    @app.get("/api/me")
    def me():
        """
        endpoint para checar a autenticação atual.
        fluxo: 
            lê dados da sessão
            se não houver user_id, considera não autenticado
            caso contrário, retorna authenticated=True e o email
        """
        
        user_id = session.get("user_id")
        user_email = session.get("user_email")
        
        if not user_id:
            return jsonify({"authenticated": False}), 200
        return jsonify({"authenticated": True, "email": user_email}), 200
    
    @app.post("/api/logout")
    def logout():
        """
        endpoint de logout
        fluxo:
            limpa completamente a sessão
            retorna mensagem de sucesso
        """
        
        session.clear()
        return jsonify({"message": "Logout efetuado"}), 200
    
    @app.get("/")
    def serve_index():
        # Serve o arquivo index.html como página inicial
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        index_file = os.path.join(base_dir, "index.html")
        return send_file(index_file, mimetype="text/html")

    @app.get("/auth")
    def serve_auth():
        # Serve a tela de autenticação em /auth
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        auth_file = os.path.join(base_dir, "app", "views", "auth.html")
        return send_file(auth_file, mimetype="text/html")
        
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    
    @app.get('/css/<path:filename>')
    def serve_css(filename):
        dir_path = os.path.join(base_dir, "app", "views", "css")
        return send_from_directory(dir_path, filename)
    
    
    @app.get('/js/<path:filename>')
    def serve_js(filename):
        dir_path = os.path.join(base_dir, "app", "views", "js")
        return send_from_directory(dir_path, filename)

    # Rotas adicionais compatíveis com os caminhos atuais do seu HTML
    # Ex.: /app/views/css/home.css
    @app.get('/app/views/css/<path:filename>')
    def serve_views_css(filename):
        dir_path = os.path.join(base_dir, "app", "views", "css")
        return send_from_directory(dir_path, filename)

    # Ex.: /app/views/js/auth.js
    @app.get('/app/views/js/<path:filename>')
    def serve_views_js(filename):
        dir_path = os.path.join(base_dir, "app", "views", "js")
        return send_from_directory(dir_path, filename)

    # Ex.: /app/img/estgLog1.png
    @app.get('/app/img/<path:filename>')
    def serve_app_img(filename):
        dir_path = os.path.join(base_dir, "app", "img")
        return send_from_directory(dir_path, filename)

    # Ex.: /app/views/auth.html (link atual do botão "Candidate-se")
    @app.get('/app/views/auth.html')
    def serve_auth_html_legacy():
        auth_file = os.path.join(base_dir, "app", "views", "auth.html")
        return send_file(auth_file, mimetype="text/html")
    
    #retorna a instância do app configurada
    return app

if __name__ == "__main__":
    app = create_app()
    
    app.run(host="127.0.0.1", port=5000, debug=True)