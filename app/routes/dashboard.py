from flask import Blueprint, jsonify
from app.utils.database import get_db_connection
from app.utils.auth import token_required

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/stats', methods=['GET'])
@token_required
def get_stats(current_user):
    """Retorna estatísticas gerais do sistema."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Total de famílias
            cursor.execute("SELECT COUNT(*) as total FROM families")
            total_families = cursor.fetchone()['total']
            
            # Total de doações (cestas recebidas)
            cursor.execute("SELECT COALESCE(SUM(quantity), 0) as total FROM donations")
            total_donations = cursor.fetchone()['total']
            
            # Total de distribuições (cestas distribuídas)
            cursor.execute("SELECT COALESCE(SUM(quantity), 0) as total FROM distributions")
            total_distributions = cursor.fetchone()['total']
            
            # Cestas disponíveis
            available_baskets = total_donations - total_distributions
            
            # Últimas distribuições
            cursor.execute("""
                SELECT id, family_name, pickup_person_name, quantity, date, created_at
                FROM distributions
                ORDER BY created_at DESC
                LIMIT 5
            """)
            recent_distributions = cursor.fetchall()
            
            recent_dist_list = []
            for dist in recent_distributions:
                recent_dist_list.append({
                    'id': str(dist['id']),
                    'familyName': dist['family_name'],
                    'pickupPersonName': dist['pickup_person_name'],
                    'quantity': dist['quantity'],
                    'date': dist['date'].isoformat(),
                    'createdAt': dist['created_at'].isoformat()
                })
            
            cursor.close()
            
            return jsonify({
                'totalFamilies': total_families,
                'totalDonations': total_donations,
                'totalDistributions': total_distributions,
                'availableBaskets': available_baskets,
                'recentDistributions': recent_dist_list
            }), 200
    
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar estatísticas: {str(e)}'}), 500
