#!/usr/bin/env python3
import requests
import time
import json
import psycopg2
from typing import Dict, List

API_BASE_URL = "http://localhost:8000"
DATABASE_URL = "postgresql://postgres:PLLfLHcQoBSLlPmsQLRytEtDOmBQptwi@yamanote.proxy.rlwy.net:28818/railway"

def get_all_influencers_without_tiktok_id() -> List[Dict]:
    """Get all influencers that need TikTok ID sync"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    query = """
    SELECT eldorado_username, tiktok_username 
    FROM influencer_ids 
    WHERE tiktok_username IS NOT NULL 
    AND (tiktok_id IS NULL OR tiktok_id = '')
    ORDER BY eldorado_username;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return [{"eldorado_username": row[0], "tiktok_username": row[1]} for row in results]

def sync_tiktok_id_via_api(eldorado_username: str) -> Dict:
    """Get TikTok ID via API"""
    try:
        url = f"{API_BASE_URL}/api/v1/influencers/{eldorado_username}/sync-tiktok-id"
        response = requests.post(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'tiktok_id': data.get('tiktok_id')
            }
        else:
            return {
                'success': False,
                'error': response.text
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def process_all_influencers():
    """Process all influencers and collect results"""
    
    print("🔍 Buscando todos os influenciadores sem TikTok ID...")
    influencers = get_all_influencers_without_tiktok_id()
    
    if not influencers:
        print("✅ Todos os influenciadores já possuem TikTok ID!")
        return
    
    print(f"📊 Encontrados {len(influencers)} influenciadores para processar")
    print("🚀 Iniciando coleta de TikTok IDs...")
    
    results = []
    success_count = 0
    error_count = 0
    
    for i, influencer in enumerate(influencers, 1):
        username = influencer['eldorado_username']
        tiktok_username = influencer['tiktok_username']
        
        print(f"[{i}/{len(influencers)}] Processando: {username} (@{tiktok_username})")
        
        result = sync_tiktok_id_via_api(username)
        
        if result['success']:
            print(f"  ✅ TikTok ID: {result['tiktok_id']}")
            results.append({
                'eldorado_username': username,
                'tiktok_id': result['tiktok_id'],
                'status': 'success'
            })
            success_count += 1
        else:
            print(f"  ❌ Erro: {result['error']}")
            results.append({
                'eldorado_username': username,
                'tiktok_id': None,
                'status': 'failed',
                'error': result['error']
            })
            error_count += 1
        
        # Delay to avoid rate limiting
        if i < len(influencers):
            time.sleep(0.5)
    
    print(f"\n{'='*60}")
    print(f"COLETA FINALIZADA")
    print(f"{'='*60}")
    print(f"Total processados: {len(influencers)}")
    print(f"Sucessos: {success_count}")
    print(f"Erros: {error_count}")
    
    # Save results to file
    with open('tiktok_ids_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📁 Resultados salvos em: tiktok_ids_results.json")
    
    return results

def update_database_with_results(results: List[Dict]):
    """Update database with collected TikTok IDs"""
    if not results:
        print("❌ Nenhum resultado para atualizar")
        return
    
    print(f"\n🔄 Atualizando banco de dados com {len(results)} registros...")
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    success_updates = 0
    failed_updates = 0
    
    for result in results:
        if result['status'] == 'success' and result['tiktok_id']:
            try:
                update_query = """
                UPDATE influencer_ids 
                SET tiktok_id = %s, updated_at = NOW()
                WHERE eldorado_username = %s;
                """
                
                cursor.execute(update_query, (result['tiktok_id'], result['eldorado_username']))
                success_updates += 1
                
            except Exception as e:
                print(f"❌ Erro ao atualizar {result['eldorado_username']}: {e}")
                failed_updates += 1
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Banco atualizado:")
    print(f"  - Sucessos: {success_updates}")
    print(f"  - Falhas: {failed_updates}")

def main():
    print("🎯 Sincronização Batch de TikTok IDs - El Dorado")
    print("=" * 60)
    
    # Step 1: Process all influencers
    results = process_all_influencers()
    
    if not results:
        return
    
    # Step 2: Update database
    update_database_with_results(results)
    
    print(f"\n🎉 Processo concluído!")

if __name__ == "__main__":
    main()