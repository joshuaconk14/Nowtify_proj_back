from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/aa', methods=['GET'])
def home():
    return jsonify({'message': 'homepage'}), 201


if __name__ == "__main__":
    app.run()