"""
API1 - Flask application running on port 5000
Serves / endpoints and /health for load balancer health checks.
"""

from flask import Flask, jsonify
import socket
import datetime

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "api1",
        "hostname": socket.gethostname(),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }), 200


@app.route("/")
def root():
    return jsonify({
        "service": "api1",
        "message": "Welcome to API1",
        "hostname": socket.gethostname(),
        "endpoints": ["/", "/status", "/health"]
    }), 200


@app.route("/status")
def status():
    return jsonify({
        "service": "api1",
        "status": "running",
        "port": 5000,
        "hostname": socket.gethostname(),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
