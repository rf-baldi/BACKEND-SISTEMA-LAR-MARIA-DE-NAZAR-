import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DATABASE_URL = os.getenv('DATABASE_URL')

@contextmanager
def get_db_connection():
    """Context manager para conexão com o banco de dados."""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Inicializa o banco de dados criando as tabelas necessárias."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de famílias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS families (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                father_name VARCHAR(255),
                mother_name VARCHAR(255),
                number_of_children INTEGER DEFAULT 0,
                is_employed BOOLEAN DEFAULT FALSE,
                receives_government_aid BOOLEAN DEFAULT FALSE,
                government_aid_type VARCHAR(255),
                has_critical_factor BOOLEAN DEFAULT FALSE,
                critical_factor_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de filhos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS children (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                family_id UUID REFERENCES families(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                age INTEGER NOT NULL
            )
        """)
        
        # Tabela de doações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS donations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                responsible_name VARCHAR(255) NOT NULL,
                cpf VARCHAR(14) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                quantity INTEGER NOT NULL,
                type VARCHAR(50) DEFAULT 'entry',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de distribuições
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS distributions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                family_id UUID REFERENCES families(id) ON DELETE CASCADE,
                family_name VARCHAR(255) NOT NULL,
                pickup_person_name VARCHAR(255) NOT NULL,
                quantity INTEGER NOT NULL,
                date TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Criar usuário padrão (admin/admin123) se não existir
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()['count'] == 0:
            import bcrypt
            password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                ('admin', password_hash)
            )
        
        conn.commit()
        cursor.close()
