from flask import Flask, request, jsonify
from functools import wraps
import datetime

app = Flask(__name__)

def validate_date_format(date_str):
    try:
        datetime.datetime.strptime(date_str, "%d-%m-%Y")
        return True
    except ValueError:
        return False

def validate_json_payload(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "Invalid JSON payload"}), 422
        data = request.get_json()
        if not isinstance(data.get("date"), str) or not validate_date_format(data["date"]):
            return jsonify({"error": "Invalid 'date' format"}), 422
        if not isinstance(data.get("amount"), (int, float)):
            return jsonify({"error": "Invalid 'amount' type"}), 422
        return f(*args, **kwargs)
    return decorated_function

def validate_query_params(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        if not start_date or not end_date:
            return jsonify({"error": "Missing query parameters"}), 422
        if not validate_date_format(start_date) or not validate_date_format(end_date):
            return jsonify({"error": "Invalid date format in query parameters"}), 422
        return f(*args, **kwargs)
    return decorated_function

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != "user" or auth.password != "password":
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route("/client/<client_id>", methods=["POST"])
@authenticate
@validate_query_params
@validate_json_payload
def handle_request(client_id):
    data = request.get_json()
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    return jsonify({
        "client_id": client_id,
        "received_date": data["date"],
        "amount": data["amount"],
        "query_start_date": start_date,
        "query_end_date": end_date
    }), 200

if __name__ == "__main__":
    app.run(debug=True)
