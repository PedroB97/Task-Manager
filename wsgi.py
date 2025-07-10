import os
from app import create_app  # Importe diretamente do app.py

# Cria a instância da aplicação Flask
application = create_app()

if __name__ == "__main__":
    application.run()
