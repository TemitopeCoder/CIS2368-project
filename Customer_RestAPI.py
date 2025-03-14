from flask import Flask, jsonify, request
from mysql import create_connection, execute_query, execute_read_query

app = Flask(__name__)
Debug = True

conn = create_connection()

