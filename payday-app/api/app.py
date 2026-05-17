import os
import uuid
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import redis

app = Flask(__name__)
CORS(app)  # Secures and allows Frontend cross-origin communication

# Infrastructure Connections (Values injected securely via environment variables)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "payday_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "vault_secret_pass")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

@app.route('/api/v1/payments', methods=['POST'])
def initiate_payment():
    data = request.get_json()
    
    # Input Validation (Security Gate)
    if not data or 'amount' not in data or 'user_id' not in data:
        return jsonify({"error": "Malformed payload. Missing amount or user_id"}), 400
    
    tx_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
    amount = float(data['amount'])
    user_id = data['user_id']

    try:
        # Step 1: Log to Stateful Database as PENDING
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO transactions (transaction_id, user_id, amount, status) VALUES (%s, %s, %s, 'PENDING');",
            (tx_id, user_id, amount)
        )
        conn.commit()
        cur.close()
        conn.close()

        # Step 2: Push Asynchronously to Redis Broker (Fast handoff)
        r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
        payload = {"transaction_id": tx_id, "amount": amount, "user_id": user_id}
        r.rpush("payment_queue", json.dumps(payload))

        # Instantly respond to frontend while processing happens in background
        return jsonify({
            "status": "ACCEPTED",
            "message": "Payment queued for processing securely.",
            "transaction_id": tx_id
        }), 202

    except Exception as e:
        return jsonify({"error": "Internal infrastructure failure", "details": str(e)}), 500

@app.route('/api/v1/payments/<tx_id>', methods=['GET'])
def check_status(tx_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT status, amount, created_at FROM transactions WHERE transaction_id = %s;", (tx_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            return jsonify({"transaction_id": tx_id, "status": result[0], "amount": float(result[1])})
        return jsonify({"error": "Transaction not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Bound to 0.0.0.0 to make it accessible inside docker/kubernetes container routing
    app.run(host='0.0.0.0', port=5000, debug=True)
