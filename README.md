# RAG Chatbot - PDF & URL Knowledge Base

A full-stack RAG (Retrieval-Augmented Generation) chatbot application that allows users to upload PDFs or paste URLs to build a knowledge base and chat with AI about the content.

## 🚀 Features

- **PDF Upload**: Upload PDF files and extract text content
- **URL Scraping**: Paste website URLs to scrape and index content
- **Vector Database**: Store embeddings in ChromaDB for fast semantic search
- **RAG Pipeline**: Retrieve relevant context and generate AI-powered answers
- **Chat Interface**: Beautiful, modern UI for interacting with your knowledge base
- **Persistent Storage**: Data persists between sessions

## 🛠️ Tech Stack

### Frontend
- **Next.js 14** (React + TypeScript)
- **Tailwind CSS** for styling
- **Vercel** for deployment

### Backend
- **FastAPI** (Python)
- **ChromaDB** for vector storage
- **SentenceTransformers** for embeddings (all-MiniLM-L6-v2)
- **PyMuPDF** for PDF extraction
- **Newspaper3k** + **BeautifulSoup** for URL scraping
- **Groq API** or **Hugging Face Inference API** for LLM

### Deployment
- Frontend: **Vercel** (free tier)
- Backend: **Railway** free tier (or Vercel Serverless Functions)
- Database: **ChromaDB** (stored in backend filesystem)

## 📋 Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Groq API key (get one at [console.groq.com](https://console.groq.com)) OR Hugging Face API key

## 🚀 Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.example .env
```

5. Edit `.env` and add your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
USE_GROQ=true
CHROMA_DB_PATH=./chroma_db
```

6. Run the backend server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file (optional, defaults to localhost:8000):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📦 Deployment

### Backend on Railway

1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repository
3. Set the root directory to `backend`
4. Add environment variables in Railway dashboard
5. Railway will automatically deploy

### Frontend on Vercel

1. Push your code to GitHub
2. Import project in [Vercel](https://vercel.com)
3. Set root directory to `frontend`
4. Add environment variable `NEXT_PUBLIC_API_URL` pointing to your Railway backend URL
5. Deploy!

## 🎯 Usage

1. **Upload a PDF**: Click "Choose PDF" and select a PDF file
2. **Add a URL**: Paste a website URL and click the link icon
3. **Ask Questions**: Type questions in the chat interface about your uploaded content
4. **View Sources**: Each answer shows the sources it retrieved from

## 📁 Project Structure

```
RAG_chatBot/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── services/
│   │   ├── pdf_extractor.py   # PDF text extraction
│   │   ├── url_scraper.py     # URL content scraping
│   │   ├── vector_store.py    # ChromaDB operations
│   │   └── rag_service.py     # RAG pipeline & LLM
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Main chat interface
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── package.json
│   └── next.config.js
└── README.md
```

## 🔧 Configuration

### LLM Provider

You can switch between Groq and Hugging Face by setting `USE_GROQ=true` or `USE_GROQ=false` in your `.env` file.

**Groq** (Recommended):
- Faster responses
- Free tier with generous limits
- Better for production

**Hugging Face**:
- Free inference API
- May have rate limits
- Good fallback option

## 🐛 Troubleshooting

- **PDF not uploading**: Ensure the file is a valid PDF and not corrupted
- **URL scraping fails**: Some websites block scraping. Try a different URL or check if the site requires authentication
- **No responses from LLM**: Check your API keys in `.env` file
- **ChromaDB errors**: Ensure the `chroma_db` directory has write permissions

## 📝 License

MIT License - feel free to use this project for your own purposes!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

