#!/bin/bash

# Exit on error
set -e

# Hiển thị banner
echo "=================================================="
echo "     TOKEN DATA API - SETUP AND RUN SCRIPT        "
echo "=================================================="
echo

# Set absolute paths with full path
CURRENT_DIR="$(pwd)"
BASE_DIR="/Users/user/Desktop/Data-Engineering/Day6"
API_DIR="$BASE_DIR/scripts/api"
SCRIPTS_DIR="$BASE_DIR/scripts"

echo "Current directory: $CURRENT_DIR"
echo "Base directory: $BASE_DIR"
echo "API directory: $API_DIR"
echo "Scripts directory: $SCRIPTS_DIR"
echo

# Thay đổi đường dẫn tới thư mục API
cd "$API_DIR"
echo "Working directory: $(pwd)"
echo

# Tạo môi trường ảo nếu chưa tồn tại
if [ ! -d "venv" ]; then
    echo "Creating new virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created successfully."
else
    echo "Found existing virtual environment."
fi
echo

# Kích hoạt môi trường ảo
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated."
echo

# Cài đặt các gói phụ thuộc
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed successfully."
echo

# Kiểm tra các gói đã cài đặt
echo "Checking installed packages:"
pip list | grep -E 'fastapi|uvicorn|sqlalchemy|pandas|psycopg2'
echo

# Initialize the database using the init_db.py script
echo "Initializing database..."
cd "$SCRIPTS_DIR"
echo "Changed to scripts directory: $(pwd)"

# Run the database initialization script
python3 "$SCRIPTS_DIR/init_db.py"

if [ $? -ne 0 ]; then
    echo "❌ Database initialization failed!"
    exit 1
fi
echo "✅ Database initialized successfully."
echo

# Return to the API directory
cd "$API_DIR"

# Hiển thị thông tin về API
echo "=================================================="
echo "TOKEN DATA API ENDPOINTS:"
echo "- Root: http://localhost:8000/"
echo "- Health Check: http://localhost:8000/api/health"
echo "- List Tokens: http://localhost:8000/api/tokens"
echo "- Token by Address: http://localhost:8000/api/tokens/address/{address}"
echo "=================================================="
echo

# Chạy máy chủ API
echo "Starting API server..."
echo "API will be available at http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo
python3 main.py