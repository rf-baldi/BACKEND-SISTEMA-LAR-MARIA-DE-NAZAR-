from flask import Blueprint, request, jsonify
from app.utils.database import get_db_connection
from app.utils.auth import token_required
from datetime import datetime

distributions_bp = Blueprint('distributions', __name__, url_prefix='/api/distributions')

@distributions_bp.route('', methods=['GET'])
@token_required
def get_distributions(current_user):
    """Lista todas as distribuições."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, family_id, family_name, pickup_person_name, quantity, date, created_at
                FROM distributions
                ORDER BY created_at DESC
            """)
            distributions = cursor.fetchall()
            
            result = []
            for distribution in distributions:
                dist_dict = dict(distribution)
                dist_dict['id'] = str(dist_dict['id'])
                dist_dict['familyId'] = str(dist_dict.pop('family_id'))
                dist_dict['familyName'] = dist_dict.pop('family_name')
                dist_dict['pickupPersonName'] = dist_dict.pop('pickup_person_name')
                dist_dict['date'] = dist_dict['date'].isoformat()
                dist_dict['createdAt'] = dist_dict.pop('created_at').isoformat()
                result.append(dist_dict)
            
            cursor.close()
            return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar distribuições: {str(e)}'}), 500

@distributions_bp.route('', methods=['POST'])
@token_required
def create_distribution(current_user):
    """Cria uma nova distribuição."""
    data = request.get_json()
    
    if not data or not data.get('familyId') or not data.get('quantity'):
        return jsonify({'error': 'Dados incompletos'}), 400
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar se há cestas suficientes em estoque
            cursor.execute("SELECT COALESCE(SUM(quantity), 0) as total FROM donations")
            total_donations = cursor.fetchone()['total']
            
            cursor.execute("SELECT COALESCE(SUM(quantity), 0) as total FROM distributions")
            total_distributions = cursor.fetchone()['total']
            
            available = total_donations - total_distributions
            
            if available < data['quantity']:
                return jsonify({'error': f'Cestas insuficientes. Disponível: {available}'}), 400
            
            # Criar distribuição
            distribution_date = datetime.fromisoformat(data['date'].replace('Z', '+00:00')) if data.get('date') else datetime.now()
            
            cursor.execute("""
                INSERT INTO distributions (family_id, family_name, pickup_person_name, quantity, date)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, created_at
            """, (
                data['familyId'],
                data['familyName'],
                data['pickupPersonName'],
                data['quantity'],
                distribution_date
            ))
            
            distribution = cursor.fetchone()
            conn.commit()
            cursor.close()
            
            return jsonify({
                'id': str(distribution['id']),
                'familyId': data['familyId'],
                'familyName': data['familyName'],
                'pickupPersonName': data['pickupPersonName'],
                'quantity': data['quantity'],
                'date': distribution_date.isoformat(),
                'createdAt': distribution['created_at'].isoformat()
            }), 201
    
    except Exception as e:
        return jsonify({'error': f'Erro ao criar distribuição: {str(e)}'}), 500

@distributions_bp.route('/total', methods=['GET'])
@token_required
def get_total_distributions(current_user):
    """Retorna o total de cestas distribuídas."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COALESCE(SUM(quantity), 0) as total FROM distributions")
            result = cursor.fetchone()
            
            cursor.close()
            return jsonify({'total': result['total']}), 200
    
    except Exception as e:
        return jsonify({'error': f'Erro ao calcular total de distribuições: {str(e)}'}), 500
