from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

def create_app():
    """Factory function para criar a aplicação Flask."""
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configurar CORS
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    CORS(app, resources={
        r"/api/*": {
            "origins": [frontend_url, "http://localhost:5173", "http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.families import families_bp
    from app.routes.donations import donations_bp
    from app.routes.distributions import distributions_bp
    from app.routes.dashboard import dashboard_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(families_bp)
    app.register_blueprint(donations_bp)
    app.register_blueprint(distributions_bp)
    app.register_blueprint(dashboard_bp)
    
    # Rota de health check
    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'message': 'Backend de Cestas Básicas está funcionando!'}, 200
    
    @app.route('/')
    def index():
        return {
            'message': 'API do Sistema de Gerenciamento de Cestas Básicas',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'families': '/api/families',
                'donations': '/api/donations',
                'distributions': '/api/distributions',
                'dashboard': '/api/dashboard'
            }
        }, 200
    
    return app
