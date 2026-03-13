#!/bin/bash
# Simple HTTP server for the Timefold Analytics Dashboard

PORT=8000
HOST="localhost"

echo "================================================"
echo "📊 Timefold FSR Analytics Dashboard Server"
echo "================================================"
echo ""
echo "Starting server on http://${HOST}:${PORT}"
echo ""
echo "Open your browser to:"
echo "  👉  http://${HOST}:${PORT}"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "================================================"
echo ""

# Check if dashboard_data.json exists
if [ ! -f "dashboard_data.json" ]; then
    echo "⚠️  Warning: dashboard_data.json not found!"
    echo ""
    echo "To generate it, run:"
    echo "  cd ../recurring-visits/scripts"
    echo "  python3 generate_dashboard_data.py"
    echo ""
    echo "Starting server anyway (will show sample data)..."
    echo ""
fi

# Start Python HTTP server
python3 -m http.server $PORT
