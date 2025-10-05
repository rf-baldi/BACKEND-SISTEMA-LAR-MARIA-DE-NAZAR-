from flask import Blueprint, request, jsonify
from app.utils.database import get_db_connection
from app.utils.auth import verify_password, generate_token, token_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint de login."""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username e password são obrigatórios'}), 400
    
    username = data['username']
    password = data['password']
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, password_hash FROM users WHERE username = %s",
                (username,)
            )
            user = cursor.fetchone()
            cursor.close()
            
            if not user:
                return jsonify({'error': 'Credenciais inválidas'}), 401
            
            if not verify_password(password, user['password_hash']):
                return jsonify({'error': 'Credenciais inválidas'}), 401
            
            # Gerar token JWT
            token = generate_token(str(user['id']), user['username'])
            
            return jsonify({
                'token': token,
                'user': {
                    'id': str(user['id']),
                    'username': user['username']
                }
            }), 200
    
    except Exception as e:
        return jsonify({'error': f'Erro ao fazer login: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Retorna informações do usuário autenticado."""
    return jsonify({
        'user': {
            'id': current_user['user_id'],
            'username': current_user['username']
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Endpoint de logout (apenas simbólico, o token é invalidado no frontend)."""
    return jsonify({'message': 'Logout realizado com sucesso'}), 200
