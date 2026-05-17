import os
import time
import json
import random
import psycopg2
import redis

# Dynamically injected endpoints via K8s Environment Variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "payday_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "vault_secret_pass")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

def process_background_jobs():
    print("Worker activated. Polling payment broker queue natively...", flush=True)
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
    
    while True:
        # Blocks and idles efficiently until a task drops into the Redis tray
        _, message = r.blpop("payment_queue")
        job = json.loads(message.decode('utf-8'))
        tx_id = job['transaction_id']
        
        print(f"[PROCESSING] Resolving banking gateway authorization for {tx_id}...", flush=True)
        time.sleep(3) # Simulate banking API processing latency
        
        # Simulate business outcome logic (90% Success)
        final_status = "SUCCESSFUL" if random.random() > 0.1 else "FAILED"

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE transactions SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE transaction_id = %s;",
                (final_status, tx_id)
            )
            conn.commit()
            cur.close()
            conn.close()
            print(f"[COMPLETED] {tx_id} safely synced to ledger as {final_status}.", flush=True)
        except Exception as e:
            print(f"[ERROR] Database sync failed for transaction {tx_id}: {str(e)}", flush=True)

if __name__ == '__main__':
    process_background_jobs()
