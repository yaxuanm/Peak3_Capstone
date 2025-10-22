#!/bin/bash
# Peak3 Backend Startup Script

# Update system
sudo yum update -y

# Install Python 3
sudo yum install python3 python3-pip -y

# Install git
sudo yum install git -y

# Create app directory
mkdir -p /home/ec2-user/peak3-backend
cd /home/ec2-user/peak3-backend

# Copy application files (you'll need to upload them)
# For now, we'll create a simple test

# Install Python dependencies
pip3 install flask flask-cors pandas openpyxl requests python-dotenv pyyaml

# Create a simple test server
cat > test_server.py << 'EOF'
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return jsonify({"message": "Peak3 Backend is running on AWS!"})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "service": "peak3-backend"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
EOF

# Start the server
python3 test_server.py
