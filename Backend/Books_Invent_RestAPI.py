from flask import Flask, jsonify, request
from mysql import create_connection, execute_query, execute_read_query

app = Flask(__name__)
Debug = True

conn = create_connection()

@app.route('/api/books/inventory', methods=['GET'])

def view_books():
    query = "SELECT * FROM books"
    books = execute_read_query(conn,query)
    return books

@app.route('/api/books/add', methods=['POST'])

def add_books():
    data = request.get_json()
    required_fields = [ "title", "author", "genre", "status"]

    if not all([field in data for field in required_fields]):
        return jsonify({"error": "Missing data"}), 402
    
    add_title = data["title"]
    add_author = data["author"]
    add_genre = data["genre"]
    add_status = data["status"] 

    query = "INSERT INTO books (title, author, genre, status) VALUES (%s, %s, %s, %s)"
    values= (add_title, add_author, add_genre, add_status)  

    execute_query(conn, query, values)
    return jsonify({"Message":"New book added"}), 202

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
    values = (update_status, update_id , update_title, update_author, update_genre)

    execute_query(conn, query, values) 

    return jsonify({"Message":"Book is available and updated"}), 203
    
@app.route('/api/books/delete/', methods=['DELETE'])
def delete_book():
    data = request.get_json()
    required_fields = ["id"]
    if not all([field in data for field in required_fields]):
        return jsonify({"error": "Missing data"}), 402

    delete_id = data["id"]

    query = "DELETE FROM books WHERE id = %s"
    values = (delete_id,)

    execute_query(conn, query, values)
    return jsonify({"Message":"Book deleted"}), 202

        








if __name__ == '__main__':
    app.run(port=7000, debug=True)