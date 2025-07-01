import os
import sys

# Adiciona o diretório atual ao sys.path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Importa a função create_app do __init__.py
from __init__ import create_app

# Cria a instância da aplicação Flask
application = create_app()

if __name__ == "__main__":
    application.run()

