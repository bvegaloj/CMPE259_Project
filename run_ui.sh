#!/bin/bash

# Launch script for SJSU Virtual Assistant UI
# Uses Groq-powered Llama-3.3-70B

echo " Starting SJSU Virtual Assistant..."
echo " Using Groq Llama-3.3-70B (Cloud)"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
 echo " Activating virtual environment..."
 source .venv/bin/activate
fi

# Check for .env file
if [ ! -f ".env" ]; then
 echo " Warning: .env file not found!"
 echo "Please create a .env file with your GROQ_API_KEY"
 echo ""
 echo "Example:"
 echo "GROQ_API_KEY=your_api_key_here"
 echo ""
 exit 1
fi

# Check for Groq API key
if ! grep -q "GROQ_API_KEY" .env; then
 echo " Warning: GROQ_API_KEY not found in .env!"
 echo "Please add your Groq API key to the .env file"
 exit 1
fi

echo " Environment configured"
echo ""
echo " Launching UI at http://localhost:8501"
echo " (Press Ctrl+C to stop)"
echo ""

# Launch Streamlit
streamlit run ui/streamlit_app.py \
 --server.port 8501 \
 --server.address localhost \
 --browser.gatherUsageStats false \
 --theme.primaryColor "#0055A2" \
 --theme.backgroundColor "#FFFFFF" \
 --theme.secondaryBackgroundColor "#F0F2F6" \
 --theme.textColor "#262730"
