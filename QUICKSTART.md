# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Get API Keys

1. **Groq API Key** (Recommended):
   - Go to [console.groq.com](https://console.groq.com)
   - Sign up for free
   - Create an API key
   - Copy the key

2. **OR Hugging Face API Key** (Alternative):
   - Go to [huggingface.co](https://huggingface.co)
   - Sign up and go to Settings > Access Tokens
   - Create a new token
   - Copy the token

### Step 2: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy env.example to .env and edit it
# Windows:
copy env.example .env
# Mac/Linux:
cp env.example .env

# Edit .env and add your API key:
# GROQ_API_KEY=your_key_here
# USE_GROQ=true

# Run the server
python main.py
```

Backend should now be running at `http://localhost:8000`

### Step 3: Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend should now be running at `http://localhost:3000`

### Step 4: Test It Out!

1. Open `http://localhost:3000` in your browser
2. Upload a PDF or paste a URL
3. Wait for it to process
4. Ask questions about the content!

## 🐛 Troubleshooting

**Backend won't start:**
- Make sure Python 3.9+ is installed
- Check that all dependencies installed correctly
- Verify your `.env` file exists and has the API key

**Frontend won't start:**
- Make sure Node.js 18+ is installed
- Run `npm install` again
- Check that the backend is running on port 8000

**API errors:**
- Verify your API keys are correct in `.env`
- Check that the backend is running
- Look at the backend terminal for error messages

## 📦 Deployment

See the main README.md for deployment instructions to Vercel and Railway.

