from flask import Flask, jsonify, request
from mysql import create_connection, execute_query, execute_read_query

app = Flask(__name__)
Debug = True

conn = create_connection()

@app.route('/api/customer/all', methods=['GET'])
def all_customers():
    query = "SELECT * FROM customers"
    customers = execute_read_query(conn, query)
    return jsonify(customers)

@app.route('/api/customer/add', methods=['POST'])
def add_customer():
    data = request.get_json()
    required_fields = ["email", "firstname","lastname","passwordhash"]
    if not all([field in data for field in required_fields]):
        return jsonify({"error": "Missing data"}), 402

    add_email = data["email"]
    add_firstname = data["firstname"]
    add_lastname = data["lastname"] 
    add_passwordhash = data["passwordhash"]

    query = "INSERT INTO customers (email, firstname, lastname, passwordhash) VALUES (%s, %s, %s, %s)"
    values = (add_email, add_firstname, add_lastname, add_passwordhash)

    execute_query(conn, query, values)
    return jsonify({"Message":"New customer added"}), 202

@app.route('/api/customer/update/', methods=['PUT'])
def update_customer():
    data = request.get_json()
    required_fields = ["email", "id"]
    if not all([field in data for field in required_fields]):
        return jsonify({"error": "Missing data"}), 402

    update_email = data["email"]
    update_id = data["id"]

    query = "UPDATE customers SET email = %s WHERE id = %s"
    values = (update_email, update_id)

    execute_query(conn, query, values)

    return jsonify({"Message":"Customer updated"}), 203

@app.route('/api/customer/delete/', methods=['DELETE'])
def delete_customer():
    data = request.get_json()
    required_fields = ["id"]
    if not all([field in data for field in required_fields]):
        return jsonify({"error": "Missing data"}), 402

    delete_id = data["id"]

    query = "DELETE FROM customers WHERE id = %s"
    values = (delete_id,)

    execute_query(conn, query, values)

    return jsonify({"Message":"Customer deleted"}), 204


if __name__ == '__main__':
    app.run(port=7000, debug=True)