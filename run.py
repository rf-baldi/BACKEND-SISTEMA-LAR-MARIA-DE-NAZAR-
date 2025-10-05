from app import create_app
from app.utils.database import init_db
import os

# Criar aplicação
app = create_app()

# Inicializar banco de dados
with app.app_context():
    try:
        init_db()
        print("✓ Banco de dados inicializado com sucesso!")
    except Exception as e:
        print(f"✗ Erro ao inicializar banco de dados: {e}")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
