from flask import Flask, jsonify, request
from mysql import create_connection, execute_query, execute_read_query
from datetime import datetime, timedelta

app = Flask(__name__)
Debug = True

conn = create_connection()

# Books Inventory

@app.route('/api/books/inventory', methods=['GET'])
def view_books():
    query = "SELECT * FROM books"
    books = execute_read_query(conn, query)
    return jsonify(books)

@app.route('/api/books/add', methods=['POST'])
def add_books():
    data = request.get_json()
    required_fields = ["title", "author", "genre", "status"]

    if not all([field in data for field in required_fields]):
        return jsonify({"error": "Missing data"}), 402
    
    add_title = data["title"]
    add_author = data["author"]
    add_genre = data["genre"]
    add_status = data["status"] 

    query = "INSERT INTO books (title, author, genre, status) VALUES (%s, %s, %s, %s)"
    values = (add_title, add_author, add_genre, add_status)  

    execute_query(conn, query, values)
    return jsonify({"Message": "New book added"}), 202

@app.route('/api/books/update', methods=['PUT'])
def update_status():
    data = request.get_json()
    required_fields = ["status", "bookid", "title", "author", "genre"]

    if not all([field in data for field in required_fields]):
        return jsonify({"error": "Missing data"}), 402

    update_status = data["status"]
    update_id = data["bookid"]
    update_title = data["title"]
    update_author = data["author"]
    update_genre = data["genre"]

    query = "UPDATE books SET status = %s, title = %s, author = %s, genre = %s WHERE bookid = %s"
    values = (update_status, update_title, update_author, update_genre, update_id)

    execute_query(conn, query, values)
    return jsonify({"Message": "Book updated"}), 203

@app.route('/api/books/delete/', methods=['DELETE'])
def delete_book():
    data = request.get_json()
    required_fields = ["id"]

    if not all([field in data for field in required_fields]):
        return jsonify({"error": "Missing data"}), 402

    delete_id = data["id"]

    query = "DELETE FROM books WHERE bookid = %s"
    values = (delete_id,)

    execute_query(conn, query, values)
    return jsonify({"Message": "Book deleted"}), 202

# Customers

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

@app.route('/api/customer/all', methods=['GET'])
def all_customers():
    query = "SELECT customerid, firstname, lastname, email FROM customers"
    customers = execute_read_query(conn, query)
    return jsonify(customers)

@app.route('/api/customer/add', methods=['POST'])
def add_customer():
    data = request.get_json()
    required_fields = ["email", "firstname", "lastname", "passwordhash"]
    if not all([field in data for field in required_fields]):
        return jsonify({"error": "Missing data"}), 402

    add_email = data["email"]
    add_firstname = data["firstname"]
    add_lastname = data["lastname"]
    add_passwordhash = hash_password(data["passwordhash"])

    query = "INSERT INTO customers (email, firstname, lastname, passwordhash) VALUES (%s, %s, %s, %s)"
    values = (add_email, add_firstname, add_lastname, add_passwordhash)

    execute_query(conn, query, values)
    return jsonify({"Message": "New customer added"}), 202

@app.route('/api/customer/update/', methods=['PUT'])
def update_customer():
    data = request.get_json()
    required_fields = ["email", "customerid", "firstname", "lastname", "passwordhash"]
    if not all([field in data for field in required_fields]):
        return jsonify({"error": "Missing data"}), 402

    update_email = data["email"]
    update_id = data["customerid"]
    update_firstname = data["firstname"]
    update_lastname = data["lastname"]
    update_passwordhash = hash_password(data["passwordhash"])

    query = "UPDATE customers SET email = %s, firstname = %s, lastname = %s, passwordhash = %s WHERE customerid = %s"
    values = (update_email, update_firstname, update_lastname, update_passwordhash, update_id)

    execute_query(conn, query, values)

    return jsonify({"Message": "Customer updated"}), 203

@app.route('/api/customer/delete/', methods=['DELETE'])
def delete_customer():
    data = request.get_json()
    required_fields = ["id"]
    if not all([field in data for field in required_fields]):
        return jsonify({"error": "Missing data"}), 402

    delete_id = data["id"]

    query = "DELETE FROM customers WHERE customerid = %s"
    values = (delete_id,)

    execute_query(conn, query, values)

    return jsonify({"Message": "Customer deleted"}), 204


# Borrowing Books

@app.route('/api/borrowing', methods=['POST'])
def books_borrow():
    data = request.get_json()
    required_fields = ["bookid", "customerid"]
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing data"}), 400

    bookid = data['bookid']
    customerid = data['customerid']

    books_query = "SELECT status FROM books WHERE bookid = %s"
    books = execute_read_query(conn, books_query, (bookid,))

    if not books:
        return jsonify({"message": "Book not found"}), 404
    
    book_status = books[0]["status"]  

    if book_status != "Available":
        return jsonify({"message": "Book is unavailable"}), 400

    customers_borrowed_query = "SELECT COUNT(*) AS count FROM borrowingrecords WHERE customerid = %s AND returndate IS NULL"
    customers_borrowed = execute_read_query(conn, customers_borrowed_query, (customerid,))

    borrowed_count = customers_borrowed[0]["count"] if customers_borrowed else 0
    if borrowed_count > 0:
        return jsonify({"message": "Customer already has a book"}), 400

    query = "INSERT INTO borrowingrecords (bookid, customerid, borrowdate) VALUES (%s, %s, %s)"
    values = (bookid, customerid, datetime.now().strftime("%Y-%m-%d"))
    execute_query(conn, query, values)

    update_query = "UPDATE books SET status = 'Borrowed' WHERE bookid = %s"
    execute_query(conn, update_query, (bookid,))

    return jsonify({"message": "Book borrowed"}), 201
    
@app.route('/api/return', methods=['POST'])
def books_return():
    data = request.get_json()
    required_fields = ["bookid", "customerid"]
    if not all([field in data for field in required_fields]):
        return jsonify({"message": "Missing data"}), 400
    
    bookid = data['bookid']
    customerid = data['customerid']

    query = "SELECT borrowdate FROM borrowingrecords WHERE bookid = %s AND customerid = %s AND returndate IS NULL"
    borrowed = execute_read_query(conn, query, (bookid, customerid))

    if not borrowed:
        return jsonify({"message": "Book not borrowed or already returned"}), 400

    borrowed_date = borrowed[0]["borrowdate"] if borrowed else None
    returndate = datetime.now().date()
        
    days_late = max((returndate - borrowed_date).days - 10, 0)
    late_fee = days_late * 1.00

    update_query = "UPDATE borrowingrecords SET returndate = %s, late_fee = %s WHERE bookid = %s AND customerid = %s"
    update_values = (returndate, late_fee, bookid, customerid)
    execute_query(conn, update_query, update_values)

    update_books_query = "UPDATE books SET status = 'Available' WHERE bookid = %s"
    book_update_values = (bookid,)
    execute_query(conn, update_books_query, book_update_values)
    
    return jsonify({"message": "Book returned", "late_fee": late_fee}), 202

@app.route('/api/borrowing/all', methods=['GET'])

def all_borrowing():
    query = '''SELECT books.bookid, books.title, customers.customerid, customers.firstname, customers.lastname, borrowingrecords.borrowdate, borrowingrecords.returndate, borrowingrecords.late_fee FROM borrowingrecords
    JOIN books ON borrowingrecords.bookid = books.bookid JOIN customers ON borrowingrecords.customerid = customers.customerid where books.status = 'Borrowed' ''' 
    borrowing = execute_read_query(conn, query)
    return jsonify(borrowing )


if __name__ == '__main__':
    app.run(port=7000, debug=True)