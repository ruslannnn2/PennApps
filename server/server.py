from flask import Flask, jsonify
from supabase import create_client, Client
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


@app.route("/server", methods=["GET"])
def home():
    return "Hello, World!"


@app.route("/health", methods=["GET"])
def health():
    try:
        
        response = "hello"
        return jsonify({"status": "ok", "supabase_connected": True}), 200
    except Exception as e:
        return jsonify({"status": "error", "supabase_connected": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)