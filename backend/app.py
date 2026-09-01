import json
import os
import razorpay
from flask import Flask, request, jsonify
from flask_cors import CORS

from nlp_parser import extract_requirements
from commitment_guard import run_verification_flow
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

CATALOG_PATH = os.path.join(os.path.dirname(__file__), "products.json")

with open(CATALOG_PATH, "r") as f:
    catalog_data = json.load(f)

PRODUCTS = catalog_data["products"]
MERCHANT = catalog_data["merchant"]

# ---- Razorpay setup ----
# Replace these two strings with your real test Key ID and Key Secret
RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET")

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "message": "CommitmentGuard AI backend is running.",
        "try": ["/api/health", "/api/products", "POST /api/verify", "POST /api/create-order"]
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "merchant": MERCHANT["name"]})


@app.route("/api/verify", methods=["POST"])
def verify():
    body = request.get_json(force=True) or {}
    buyer_request = body.get("request", "").strip()

    if not buyer_request:
        return jsonify({"error": "Missing 'request' field"}), 400

    requirements = extract_requirements(buyer_request)
    result = run_verification_flow(PRODUCTS, requirements)
    result["buyer_request"] = buyer_request
    result["merchant"] = MERCHANT

    return jsonify(result)


@app.route("/api/products", methods=["GET"])
def list_products():
    return jsonify({"merchant": MERCHANT, "products": PRODUCTS})


@app.route("/api/create-order", methods=["POST"])
def create_order():
    body = request.get_json(force=True) or {}
    amount_rupees = body.get("amount")

    if amount_rupees is None:
        return jsonify({"error": "Missing 'amount' field"}), 400

    order = razorpay_client.order.create({
        "amount": int(amount_rupees * 100),  # Razorpay expects paise
        "currency": "INR",
        "payment_capture": 1
    })

    return jsonify({
        "order_id": order["id"],
        "amount": amount_rupees,
        "key_id": RAZORPAY_KEY_ID
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))