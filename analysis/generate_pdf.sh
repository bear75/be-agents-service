#!/bin/bash
# Generate PDF from dashboard using headless Chrome

OUTPUT_FILE="Caire_AI_Kampanjanalys_$(date +%Y-%m-%d).pdf"
URL="http://localhost:8000/index.html"

echo "📄 Genererar PDF från dashboard..."
echo "URL: $URL"
echo "Output: $OUTPUT_FILE"

# Check if Chrome is available
if command -v /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome &> /dev/null; then
    CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif command -v chromium &> /dev/null; then
    CHROME="chromium"
else
    echo "❌ Chrome/Chromium not found. Please install Google Chrome."
    exit 1
fi

# Generate PDF with optimal settings
"$CHROME" \
    --headless \
    --disable-gpu \
    --print-to-pdf="$OUTPUT_FILE" \
    --print-to-pdf-no-header \
    --no-margins \
    --run-all-compositor-stages-before-draw \
    --virtual-time-budget=10000 \
    "$URL"

if [ -f "$OUTPUT_FILE" ]; then
    echo "✅ PDF genererad: $OUTPUT_FILE"
    echo "📊 Storlek: $(ls -lh "$OUTPUT_FILE" | awk '{print $5}')"
    open "$OUTPUT_FILE"
else
    echo "❌ Misslyckades att generera PDF"
    exit 1
fi
