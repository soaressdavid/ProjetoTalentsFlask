# flask_backend/__init__.py
# -----------------------------------------------------------------------------
# Este arquivo marca o diretório 'flask_backend' como um pacote Python.
# Sem ele, ao tentar 'from flask_backend.db import ...', o Python pode não
# conseguir resolver o pacote quando você executa o app diretamente.
# -----------------------------------------------------------------------------

# Opcionalmente, você pode expor objetos úteis aqui.
# Ex.: from .db import db
#      from .models import User
# Isso permitiria 'from flask_backend import db, User' em outros módulos.
# Não é obrigatório; é apenas uma conveniência.