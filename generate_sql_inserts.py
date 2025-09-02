#!/usr/bin/env python3
import csv
import uuid
from datetime import datetime

def read_csv_and_generate_sql(csv_file_path: str):
    """Read CSV and generate SQL INSERT statements"""
    
    print("📖 Lendo CSV e gerando comandos SQL...")
    
    sql_statements = []
    
    # Header comments
    sql_statements.append("-- Inserção de influenciadores do El Dorado")
    sql_statements.append(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql_statements.append(f"-- Total de registros: será calculado")
    sql_statements.append("")
    
    # Begin transaction
    sql_statements.append("BEGIN;")
    sql_statements.append("")
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        count = 0
        
        for row in reader:
            count += 1
            
            # Dados do influenciador
            first_name = row['Nome'].replace("'", "''")  # Escape single quotes
            eldorado_username = row['Nome'].replace("'", "''")
            tiktok_username = row['tiktok @'].replace("'", "''") if row['tiktok @'] else None
            country = row['Pais'].replace("'", "''") if row['Pais'] else None
            owner = row['Owner'].replace("'", "''")
            phone = None if row['telefone'] == 'null' else row['telefone']
            
            # INSERT na tabela influencers
            sql_statements.append(f"-- [{count}] Influencer: {eldorado_username}")
            
            insert_influencer = f"""INSERT INTO influencers (first_name, eldorado_username, phone, country, owner, status, created_at, updated_at) 
VALUES ('{first_name}', '{eldorado_username}', {f"'{phone}'" if phone else 'NULL'}, '{country}', '{owner}', 'active', NOW(), NOW())
ON CONFLICT (eldorado_username) DO NOTHING;"""
            
            sql_statements.append(insert_influencer)
            
            # INSERT na tabela influencer_ids se tiver TikTok username
            if tiktok_username:
                insert_ids = f"""INSERT INTO influencer_ids (eldorado_username, tiktok_username, created_at, updated_at)
VALUES ('{eldorado_username}', '{tiktok_username}', NOW(), NOW())
ON CONFLICT (eldorado_username) DO UPDATE SET 
    tiktok_username = EXCLUDED.tiktok_username, 
    updated_at = EXCLUDED.updated_at;"""
                
                sql_statements.append(insert_ids)
            
            sql_statements.append("")
    
    # Commit transaction
    sql_statements.append("COMMIT;")
    sql_statements.append("")
    sql_statements.append(f"-- Processados {count} influenciadores")
    
    return sql_statements, count

def main():
    """Main function"""
    import sys
    
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "influencers_limpo.csv"
    sql_file = "insert_influencers.sql"
    
    print(f"🚀 Gerando SQL para inserção no Railway PostgreSQL...")
    print(f"📁 Arquivo CSV: {csv_file}")
    print(f"📝 Arquivo SQL: {sql_file}")
    
    try:
        # Gerar comandos SQL
        sql_statements, count = read_csv_and_generate_sql(csv_file)
        
        # Salvar em arquivo
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_statements))
        
        print(f"\n✅ Arquivo SQL gerado com sucesso!")
        print(f"📊 Total de influenciadores: {count}")
        print(f"📁 Arquivo: {sql_file}")
        
        print(f"\n🚀 Para executar no Railway:")
        print(f"1. Conecte-se ao banco: psql 'SUA_URL_RAILWAY'")
        print(f"2. Execute: \\i {sql_file}")
        print(f"")
        print(f"Ou execute diretamente:")
        print(f"psql 'SUA_URL_RAILWAY' < {sql_file}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()