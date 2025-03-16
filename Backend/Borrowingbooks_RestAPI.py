from flask import Flask, jsonify, request
from mysql import create_connection, execute_query, execute_read_query
from datetime import datetime, timedelta

app = Flask(__name__)
Debug = True

conn = create_connection()

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