# quoter.py

import json
import math
from flask import Flask, request, jsonify
from flask_cors import CORS # Added for API connection to frontend

# --- CORE BUSINESS DATA (From your final, corrected list) ---
PLANT_DATA = [
    {"id": 1, "name": "1 1/2\" Crusher Run (594-Cherokee)", "quarryId": "Q_594", "price": 14.00, "taxRate": 0.09},
    {"id": 4, "name": "#57 Stone (594-Cherokee)", "quarryId": "Q_594", "price": 17.00, "taxRate": 0.09},
    {"id": 9, "name": "Surge Stone (594-Cherokee)", "quarryId": "Q_594", "price": 15.00, "taxRate": 0.09},
    
    {"id": 10, "name": "1 1/2\" Crusher Run (71501-Laceys)", "quarryId": "Q_71501", "price": 12.00, "taxRate": 0.09},
    {"id": 12, "name": "#57 Washed (71501-Laceys)", "quarryId": "Q_71501", "price": 20.00, "taxRate": 0.09},
    
    {"id": 16, "name": "1 1/2\" Crusher Run (591-Mt Hope)", "quarryId": "Q_591", "price": 10.00, "taxRate": 0.09},
    {"id": 17, "name": "Dense Grade Base (591-Mt Hope)", "quarryId": "Q_591", "price": 11.50, "taxRate": 0.09},
    
    {"id": 14, "name": "Concrete Sand (71087-Monteagle)", "quarryId": "Q_71087", "price": 28.00, "taxRate": 0.09},
]

# --- LOCAL DISTANCE MATRIX (Simulates Geo-API lookup) ---
DISTANCE_MATRIX = {
    "Q_594": {"D_HSV_AVIA": 100, "D_DECA_SITEA": 65, "D_FLOR_B": 45},
    "Q_71501": {"D_HSV_AVIA": 40, "D_DECA_SITEA": 50, "D_FLOR_B": 120},
    "Q_591": {"D_HSV_AVIA": 110, "D_DECA_SITEA": 85, "D_FLOR_B": 60},
    "Q_71087": {"D_HSV_AVIA": 90, "D_DECA_SITEA": 100, "D_FLOR_B": 150},
}

# --- FLASK API SETUP ---
app = Flask(__name__)
CORS(app) # Allows HTML on your PC to talk to the API

def calculate_haul_rate(minutes, tons):
    """Calculates haul rate per ton using Shane's specific business logic."""
    HOURLY_RATE = 130.0
    MINIMUM_RATE = 6.0
    
    if minutes <= 0 or tons <= 0:
        return MINIMUM_RATE

    haul_rate_per_ton = (HOURLY_RATE / 60.0) * (minutes / tons)

    if haul_rate_per_ton <= MINIMUM_RATE:
        return MINIMUM_RATE
    else:
        return math.ceil(haul_rate_per_ton * 2) / 2.0

@app.route('/api/products', methods=['GET'])
def get_products():
    """Endpoint to fetch the list of all materials and their quarry info."""
    return jsonify(PLANT_DATA)
# quoter.py

import json
import math
from flask import Flask, request, jsonify
from flask_cors import CORS # Added for API connection to frontend

# --- CORE BUSINESS DATA (From your final, corrected list) ---
PLANT_DATA = [
    {"id": 1, "name": "1 1/2\" Crusher Run (594-Cherokee)", "quarryId": "Q_594", "price": 14.00, "taxRate": 0.09},
    {"id": 4, "name": "#57 Stone (594-Cherokee)", "quarryId": "Q_594", "price": 17.00, "taxRate": 0.09},
    {"id": 9, "name": "Surge Stone (594-Cherokee)", "quarryId": "Q_594", "price": 15.00, "taxRate": 0.09},
    
    {"id": 10, "name": "1 1/2\" Crusher Run (71501-Laceys)", "quarryId": "Q_71501", "price": 12.00, "taxRate": 0.09},
    {"id": 12, "name": "#57 Washed (71501-Laceys)", "quarryId": "Q_71501", "price": 20.00, "taxRate": 0.09},
    
    {"id": 16, "name": "1 1/2\" Crusher Run (591-Mt Hope)", "quarryId": "Q_591", "price": 10.00, "taxRate": 0.09},
    {"id": 17, "name": "Dense Grade Base (591-Mt Hope)", "quarryId": "Q_591", "price": 11.50, "taxRate": 0.09},
    
    {"id": 14, "name": "Concrete Sand (71087-Monteagle)", "quarryId": "Q_71087", "price": 28.00, "taxRate": 0.09},
]

# --- LOCAL DISTANCE MATRIX (Simulates Geo-API lookup) ---
DISTANCE_MATRIX = {
    "Q_594": {"D_HSV_AVIA": 100, "D_DECA_SITEA": 65, "D_FLOR_B": 45},
    "Q_71501": {"D_HSV_AVIA": 40, "D_DECA_SITEA": 50, "D_FLOR_B": 120},
    "Q_591": {"D_HSV_AVIA": 110, "D_DECA_SITEA": 85, "D_FLOR_B": 60},
    "Q_71087": {"D_HSV_AVIA": 90, "D_DECA_SITEA": 100, "D_FLOR_B": 150},
}

# --- FLASK API SETUP ---
app = Flask(__name__)
CORS(app) # Allows HTML on your PC to talk to the API

def calculate_haul_rate(minutes, tons):
    """Calculates haul rate per ton using Shane's specific business logic."""
    HOURLY_RATE = 130.0
    MINIMUM_RATE = 6.0
    
    if minutes <= 0 or tons <= 0:
        return MINIMUM_RATE

    haul_rate_per_ton = (HOURLY_RATE / 60.0) * (minutes / tons)

    if haul_rate_per_ton <= MINIMUM_RATE:
        return MINIMUM_RATE
    else:
        return math.ceil(haul_rate_per_ton * 2) / 2.0

@app.route('/api/products', methods=['GET'])
def get_products():
    """Endpoint to fetch the list of all materials and their quarry info."""
    return jsonify(PLANT_DATA)

@app.route('/api/quote', methods=['GET'])
def get_quote():
    # Parameters: destination=D_HSV_AVIA&tons=25&material_id=AUTO
    destination_id = request.args.get('destination')
    tons = float(request.args.get('tons', 25))
    material_id = request.args.get('material_id', 'AUTO')
    
    if not destination_id or tons <= 0:
        return jsonify({"error": "Missing parameters."}), 400

    optimal_cost = float('inf')
    optimal_quote = None
    
    products_to_check = PLANT_DATA

    # Check only one material if ID is provided (User Override)
    if material_id != 'AUTO':
        try:
            target_id = int(material_id)
            products_to_check = [p for p in PLANT_DATA if p['id'] == target_id]
        except ValueError:
            return jsonify({"error": "Invalid material ID format."}), 400
    
    for material in products_to_check:
        quarry_id = material['quarryId']
        
        # 1. Get RTT
        rtt = DISTANCE_MATRIX.get(quarry_id, {}).get(destination_id)
        if rtt is None:
            continue

        # 2. Calculate Costs
        haul_rate = calculate_haul_rate(rtt, tons)
        material_price = material['price']
        tax_rate = material['taxRate']
        
        cost_per_ton_pre_tax = material_price + haul_rate
        total_job_price = cost_per_ton_pre_tax * tons * (1 + tax_rate)
        
        if total_job_price < optimal_cost or material_id != 'AUTO':
            optimal_cost = total_job_price
            optimal_quote = {
                "plant": material['name'],
                "product_id": material['id'],
                "rtt_minutes": rtt,
                "haul_rate_per_ton": round(haul_rate, 2),
                "material_price": round(material_price, 2),
                "total_job_price": round(total_job_price, 2),
                "breakdown": f"(${material_price:.2f} Material + ${haul_rate:.2f} Haul) x {tons:.0f} Tons + 9% Tax"
            }
            if material_id != 'AUTO':
                break # Exit loop if user forced a specific material

    if optimal_quote:
        return jsonify(optimal_quote)
    else:
        return jsonify({"error": "No quote found for this combination. Check RTT/Plant availability."}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)
@app.route('/api/quote', methods=['GET'])
def get_quote():
    # Parameters: destination=D_HSV_AVIA&tons=25&material_id=AUTO
    destination_id = request.args.get('destination')
    tons = float(request.args.get('tons', 25))
    material_id = request.args.get('material_id', 'AUTO')
    
    if not destination_id or tons <= 0:
        return jsonify({"error": "Missing parameters."}), 400

    optimal_cost = float('inf')
    optimal_quote = None
    
    products_to_check = PLANT_DATA

    # Check only one material if ID is provided (User Override)
    if material_id != 'AUTO':
        try:
            target_id = int(material_id)
            products_to_check = [p for p in PLANT_DATA if p['id'] == target_id]
        except ValueError:
            return jsonify({"error": "Invalid material ID format."}), 400
    
    for material in products_to_check:
        quarry_id = material['quarryId']
        
        # 1. Get RTT
        rtt = DISTANCE_MATRIX.get(quarry_id, {}).get(destination_id)
        if rtt is None:
            continue

        # 2. Calculate Costs
        haul_rate = calculate_haul_rate(rtt, tons)
        material_price = material['price']
        tax_rate = material['taxRate']
        
        cost_per_ton_pre_tax = material_price + haul_rate
        total_job_price = cost_per_ton_pre_tax * tons * (1 + tax_rate)
        
        if total_job_price < optimal_cost or material_id != 'AUTO':
            optimal_cost = total_job_price
            optimal_quote = {
                "plant": material['name'],
                "product_id": material['id'],
                "rtt_minutes": rtt,
                "haul_rate_per_ton": round(haul_rate, 2),
                "material_price": round(material_price, 2),
                "total_job_price": round(total_job_price, 2),
                "breakdown": f"(${material_price:.2f} Material + ${haul_rate:.2f} Haul) x {tons:.0f} Tons + 9% Tax"
            }
            if material_id != 'AUTO':
                break # Exit loop if user forced a specific material

    if optimal_quote:
        return jsonify(optimal_quote)
    else:
        return jsonify({"error": "No quote found for this combination. Check RTT/Plant availability."}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)