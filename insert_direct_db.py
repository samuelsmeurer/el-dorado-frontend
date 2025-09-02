#!/usr/bin/env python3
import csv
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

# Database URL do Railway
DATABASE_URL = "postgresql://postgres:PLLfLHcQoBSLlPmsQLRytEtDOmBQptwi@yamanote.proxy.rlwy.net:28818/railway"

def read_csv_data(file_path: str) -> list:
    """Read influencers data from CSV file"""
    influencers = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Preparar dados conforme estrutura do banco
            influencer = {
                'first_name': row['Nome'],
                'eldorado_username': row['Nome'],  # Nome como eldorado_username
                'tiktok_username': row['tiktok @'],
                'country': row['Pais'],
                'owner': row['Owner'],
                'phone': None if row['telefone'] == 'null' else row['telefone']
            }
            influencers.append(influencer)
    
    return influencers

def connect_to_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Conexão com Railway PostgreSQL estabelecida!")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco: {e}")
        return None

def insert_influencers_direct(influencers_data: list):
    """Insert influencers directly into database"""
    
    conn = connect_to_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    success_count = 0
    error_count = 0
    
    try:
        for i, influencer in enumerate(influencers_data, 1):
            print(f"[{i}/{len(influencers_data)}] Inserindo: {influencer['eldorado_username']}")
            
            try:
                # INSERT na tabela influencers
                insert_influencer_query = """
                INSERT INTO influencers (first_name, eldorado_username, phone, country, owner, status, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (eldorado_username) DO NOTHING
                RETURNING id, eldorado_username;
                """
                
                now = datetime.utcnow()
                cursor.execute(insert_influencer_query, (
                    influencer['first_name'],
                    influencer['eldorado_username'], 
                    influencer['phone'],
                    influencer['country'],
                    influencer['owner'],
                    'active',
                    now,
                    now
                ))
                
                result = cursor.fetchone()
                if result:
                    print(f"  ✅ Influencer inserido: {influencer['eldorado_username']}")
                    
                    # Se temos tiktok_username, inserir na tabela influencer_ids
                    if influencer['tiktok_username']:
                        insert_ids_query = """
                        INSERT INTO influencer_ids (eldorado_username, tiktok_username, created_at, updated_at) 
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (eldorado_username) DO UPDATE SET
                            tiktok_username = EXCLUDED.tiktok_username,
                            updated_at = EXCLUDED.updated_at;
                        """
                        
                        cursor.execute(insert_ids_query, (
                            influencer['eldorado_username'],
                            influencer['tiktok_username'],
                            now,
                            now
                        ))
                        print(f"  ✅ TikTok username adicionado: {influencer['tiktok_username']}")
                    
                    success_count += 1
                else:
                    print(f"  ⚠️  Já existe: {influencer['eldorado_username']}")
                
            except Exception as e:
                print(f"  ❌ Erro ao inserir {influencer['eldorado_username']}: {e}")
                error_count += 1
                continue
        
        # Commit todas as mudanças
        conn.commit()
        print(f"\n{'='*50}")
        print(f"RESULTADO FINAL:")
        print(f"{'='*50}")
        print(f"Total processados: {len(influencers_data)}")
        print(f"Sucessos: {success_count}")
        print(f"Erros: {error_count}")
        print(f"✅ Transação commitada com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        conn.rollback()
        print("🔄 Rollback executado!")
        
    finally:
        cursor.close()
        conn.close()
        print("🔌 Conexão fechada.")

def main():
    """Main function"""
    import sys
    csv_file_path = sys.argv[1] if len(sys.argv) > 1 else "influencers_limpo.csv"
    
    print("🚀 Iniciando inserção direta no Railway PostgreSQL...")
    print(f"📁 Arquivo CSV: {csv_file_path}")
    
    # Ler dados do CSV
    print("\n📖 Lendo dados do CSV...")
    influencers = read_csv_data(csv_file_path)
    print(f"📊 Total de influenciadores encontrados: {len(influencers)}")
    
    # Inserir no banco
    print(f"\n💾 Iniciando inserção no banco de dados...")
    insert_influencers_direct(influencers)

if __name__ == "__main__":
    main()