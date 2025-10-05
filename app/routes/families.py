from flask import Blueprint, request, jsonify
from app.utils.database import get_db_connection
from app.utils.auth import token_required
from datetime import datetime

families_bp = Blueprint('families', __name__, url_prefix='/api/families')

@families_bp.route('', methods=['GET'])
@token_required
def get_families(current_user):
    """Lista todas as famílias."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Buscar todas as famílias
            cursor.execute("""
                SELECT id, name, father_name, mother_name, number_of_children,
                       is_employed, receives_government_aid, government_aid_type,
                       has_critical_factor, critical_factor_notes, created_at, updated_at
                FROM families
                ORDER BY created_at DESC
            """)
            families = cursor.fetchall()
            
            # Para cada família, buscar seus filhos
            result = []
            for family in families:
                cursor.execute(
                    "SELECT id, name, age FROM children WHERE family_id = %s",
                    (family['id'],)
                )
                children = cursor.fetchall()
                
                family_dict = dict(family)
                family_dict['id'] = str(family_dict['id'])
                family_dict['children'] = [
                    {
                        'id': str(child['id']),
                        'name': child['name'],
                        'age': child['age']
                    }
                    for child in children
                ]
                family_dict['createdAt'] = family_dict.pop('created_at').isoformat()
                family_dict['updatedAt'] = family_dict.pop('updated_at').isoformat()
                family_dict['fatherName'] = family_dict.pop('father_name')
                family_dict['motherName'] = family_dict.pop('mother_name')
                family_dict['numberOfChildren'] = family_dict.pop('number_of_children')
                family_dict['isEmployed'] = family_dict.pop('is_employed')
                family_dict['receivesGovernmentAid'] = family_dict.pop('receives_government_aid')
                family_dict['governmentAidType'] = family_dict.pop('government_aid_type')
                family_dict['hasCriticalFactor'] = family_dict.pop('has_critical_factor')
                family_dict['criticalFactorNotes'] = family_dict.pop('critical_factor_notes')
                
                result.append(family_dict)
            
            cursor.close()
            return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar famílias: {str(e)}'}), 500

@families_bp.route('', methods=['POST'])
@token_required
def create_family(current_user):
    """Cria uma nova família."""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Nome da família é obrigatório'}), 400
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Inserir família
            cursor.execute("""
                INSERT INTO families (
                    name, father_name, mother_name, number_of_children,
                    is_employed, receives_government_aid, government_aid_type,
                    has_critical_factor, critical_factor_notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, created_at, updated_at
            """, (
                data['name'],
                data.get('fatherName'),
                data.get('motherName'),
                data.get('numberOfChildren', 0),
                data.get('isEmployed', False),
                data.get('receivesGovernmentAid', False),
                data.get('governmentAidType'),
                data.get('hasCriticalFactor', False),
                data.get('criticalFactorNotes')
            ))
            
            family = cursor.fetchone()
            family_id = str(family['id'])
            
            # Inserir filhos
            children = []
            if data.get('children'):
                for child in data['children']:
                    cursor.execute("""
                        INSERT INTO children (family_id, name, age)
                        VALUES (%s, %s, %s)
                        RETURNING id, name, age
                    """, (family_id, child['name'], child['age']))
                    
                    child_data = cursor.fetchone()
                    children.append({
                        'id': str(child_data['id']),
                        'name': child_data['name'],
                        'age': child_data['age']
                    })
            
            conn.commit()
            cursor.close()
            
            return jsonify({
                'id': family_id,
                'name': data['name'],
                'fatherName': data.get('fatherName'),
                'motherName': data.get('motherName'),
                'numberOfChildren': data.get('numberOfChildren', 0),
                'children': children,
                'isEmployed': data.get('isEmployed', False),
                'receivesGovernmentAid': data.get('receivesGovernmentAid', False),
                'governmentAidType': data.get('governmentAidType'),
                'hasCriticalFactor': data.get('hasCriticalFactor', False),
                'criticalFactorNotes': data.get('criticalFactorNotes'),
                'createdAt': family['created_at'].isoformat(),
                'updatedAt': family['updated_at'].isoformat()
            }), 201
    
    except Exception as e:
        return jsonify({'error': f'Erro ao criar família: {str(e)}'}), 500

@families_bp.route('/<family_id>', methods=['GET'])
@token_required
def get_family(current_user, family_id):
    """Busca uma família por ID."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, father_name, mother_name, number_of_children,
                       is_employed, receives_government_aid, government_aid_type,
                       has_critical_factor, critical_factor_notes, created_at, updated_at
                FROM families
                WHERE id = %s
            """, (family_id,))
            
            family = cursor.fetchone()
            
            if not family:
                return jsonify({'error': 'Família não encontrada'}), 404
            
            # Buscar filhos
            cursor.execute(
                "SELECT id, name, age FROM children WHERE family_id = %s",
                (family_id,)
            )
            children = cursor.fetchall()
            
            family_dict = dict(family)
            family_dict['id'] = str(family_dict['id'])
            family_dict['children'] = [
                {
                    'id': str(child['id']),
                    'name': child['name'],
                    'age': child['age']
                }
                for child in children
            ]
            family_dict['createdAt'] = family_dict.pop('created_at').isoformat()
            family_dict['updatedAt'] = family_dict.pop('updated_at').isoformat()
            family_dict['fatherName'] = family_dict.pop('father_name')
            family_dict['motherName'] = family_dict.pop('mother_name')
            family_dict['numberOfChildren'] = family_dict.pop('number_of_children')
            family_dict['isEmployed'] = family_dict.pop('is_employed')
            family_dict['receivesGovernmentAid'] = family_dict.pop('receives_government_aid')
            family_dict['governmentAidType'] = family_dict.pop('government_aid_type')
            family_dict['hasCriticalFactor'] = family_dict.pop('has_critical_factor')
            family_dict['criticalFactorNotes'] = family_dict.pop('critical_factor_notes')
            
            cursor.close()
            return jsonify(family_dict), 200
    
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar família: {str(e)}'}), 500

@families_bp.route('/<family_id>', methods=['PUT'])
@token_required
def update_family(current_user, family_id):
    """Atualiza uma família."""
    data = request.get_json()
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Atualizar família
            cursor.execute("""
                UPDATE families
                SET name = %s, father_name = %s, mother_name = %s,
                    number_of_children = %s, is_employed = %s,
                    receives_government_aid = %s, government_aid_type = %s,
                    has_critical_factor = %s, critical_factor_notes = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING updated_at
            """, (
                data.get('name'),
                data.get('fatherName'),
                data.get('motherName'),
                data.get('numberOfChildren', 0),
                data.get('isEmployed', False),
                data.get('receivesGovernmentAid', False),
                data.get('governmentAidType'),
                data.get('hasCriticalFactor', False),
                data.get('criticalFactorNotes'),
                family_id
            ))
            
            result = cursor.fetchone()
            if not result:
                return jsonify({'error': 'Família não encontrada'}), 404
            
            # Deletar filhos antigos e inserir novos
            cursor.execute("DELETE FROM children WHERE family_id = %s", (family_id,))
            
            children = []
            if data.get('children'):
                for child in data['children']:
                    cursor.execute("""
                        INSERT INTO children (family_id, name, age)
                        VALUES (%s, %s, %s)
                        RETURNING id, name, age
                    """, (family_id, child['name'], child['age']))
                    
                    child_data = cursor.fetchone()
                    children.append({
                        'id': str(child_data['id']),
                        'name': child_data['name'],
                        'age': child_data['age']
                    })
            
            conn.commit()
            cursor.close()
            
            return jsonify({
                'id': family_id,
                'name': data.get('name'),
                'fatherName': data.get('fatherName'),
                'motherName': data.get('motherName'),
                'numberOfChildren': data.get('numberOfChildren', 0),
                'children': children,
                'isEmployed': data.get('isEmployed', False),
                'receivesGovernmentAid': data.get('receivesGovernmentAid', False),
                'governmentAidType': data.get('governmentAidType'),
                'hasCriticalFactor': data.get('hasCriticalFactor', False),
                'criticalFactorNotes': data.get('criticalFactorNotes'),
                'updatedAt': result['updated_at'].isoformat()
            }), 200
    
    except Exception as e:
        return jsonify({'error': f'Erro ao atualizar família: {str(e)}'}), 500

@families_bp.route('/<family_id>', methods=['DELETE'])
@token_required
def delete_family(current_user, family_id):
    """Deleta uma família."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM families WHERE id = %s RETURNING id", (family_id,))
            result = cursor.fetchone()
            
            if not result:
                return jsonify({'error': 'Família não encontrada'}), 404
            
            conn.commit()
            cursor.close()
            
            return jsonify({'message': 'Família deletada com sucesso'}), 200
    
    except Exception as e:
        return jsonify({'error': f'Erro ao deletar família: {str(e)}'}), 500
