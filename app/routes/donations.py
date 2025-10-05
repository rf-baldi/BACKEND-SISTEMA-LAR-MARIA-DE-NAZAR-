from flask import Blueprint, request, jsonify
from app.utils.database import get_db_connection
from app.utils.auth import token_required

donations_bp = Blueprint('donations', __name__, url_prefix='/api/donations')

@donations_bp.route('', methods=['GET'])
@token_required
def get_donations(current_user):
    """Lista todas as doações."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, responsible_name, cpf, phone, quantity, type, created_at
                FROM donations
                ORDER BY created_at DESC
            """)
            donations = cursor.fetchall()
            
            result = []
            for donation in donations:
                donation_dict = dict(donation)
                donation_dict['id'] = str(donation_dict['id'])
                donation_dict['responsibleName'] = donation_dict.pop('responsible_name')
                donation_dict['createdAt'] = donation_dict.pop('created_at').isoformat()
                result.append(donation_dict)
            
            cursor.close()
            return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar doações: {str(e)}'}), 500

@donations_bp.route('', methods=['POST'])
@token_required
def create_donation(current_user):
    """Cria uma nova doação."""
    data = request.get_json()
    
    if not data or not data.get('responsibleName') or not data.get('quantity'):
        return jsonify({'error': 'Dados incompletos'}), 400
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO donations (responsible_name, cpf, phone, quantity, type)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, created_at
            """, (
                data['responsibleName'],
                data.get('cpf', ''),
                data.get('phone', ''),
                data['quantity'],
                data.get('type', 'entry')
            ))
            
            donation = cursor.fetchone()
            conn.commit()
            cursor.close()
            
            return jsonify({
                'id': str(donation['id']),
                'responsibleName': data['responsibleName'],
                'cpf': data.get('cpf', ''),
                'phone': data.get('phone', ''),
                'quantity': data['quantity'],
                'type': data.get('type', 'entry'),
                'createdAt': donation['created_at'].isoformat()
            }), 201
    
    except Exception as e:
        return jsonify({'error': f'Erro ao criar doação: {str(e)}'}), 500

@donations_bp.route('/total', methods=['GET'])
@token_required
def get_total_donations(current_user):
    """Retorna o total de cestas doadas."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COALESCE(SUM(quantity), 0) as total FROM donations")
            result = cursor.fetchone()
            
            cursor.close()
            return jsonify({'total': result['total']}), 200
    
    except Exception as e:
        return jsonify({'error': f'Erro ao calcular total de doações: {str(e)}'}), 500
