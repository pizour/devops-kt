"""
API2 - Flask application running on port 5001
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
        "service": "api2",
        "hostname": socket.gethostname(),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }), 200


@app.route("/")
def root():
    return jsonify({
        "service": "api2",
        "message": "Welcome to API2",
        "hostname": socket.gethostname(),
        "endpoints": ["/", "/status", "/health"]
    }), 200


@app.route("/status")
def status():
    return jsonify({
        "service": "api2",
        "status": "running",
        "port": 5001,
        "hostname": socket.gethostname(),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
