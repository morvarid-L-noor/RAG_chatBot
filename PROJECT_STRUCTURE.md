# Project Structure

## 📁 Directory Layout

```
RAG_chatBot/
├── backend/                    # Python FastAPI backend
│   ├── main.py                # FastAPI application entry point
│   ├── requirements.txt       # Python dependencies
│   ├── Procfile              # Railway deployment config
│   ├── railway.json          # Railway configuration
│   ├── env.example           # Environment variables template
│   ├── .gitignore            # Git ignore rules
│   └── services/             # Service modules
│       ├── __init__.py
│       ├── pdf_extractor.py  # PDF text extraction using PyMuPDF
│       ├── url_scraper.py    # URL content scraping
│       ├── vector_store.py   # ChromaDB vector database operations
│       └── rag_service.py    # RAG pipeline & LLM integration
│
├── frontend/                  # Next.js frontend
│   ├── app/                  # Next.js 14 app directory
│   │   ├── page.tsx          # Main chat interface component
│   │   ├── layout.tsx        # Root layout
│   │   └── globals.css       # Global styles
│   ├── package.json          # Node.js dependencies
│   ├── tsconfig.json         # TypeScript configuration
│   ├── tailwind.config.js    # Tailwind CSS configuration
│   ├── next.config.js        # Next.js configuration
│   └── postcss.config.js     # PostCSS configuration
│
├── README.md                  # Main documentation
├── QUICKSTART.md             # Quick start guide
└── .gitignore                # Root git ignore

```

## 🔧 Key Components

### Backend Services

1. **PDF Extractor** (`services/pdf_extractor.py`)
   - Uses PyMuPDF (fitz) to extract text from PDF files
   - Handles multi-page documents

2. **URL Scraper** (`services/url_scraper.py`)
   - Uses Newspaper3k for article extraction
   - Falls back to BeautifulSoup for general web scraping
   - Handles various website structures

3. **Vector Store** (`services/vector_store.py`)
   - Manages ChromaDB persistent storage
   - Uses SentenceTransformers for embeddings (all-MiniLM-L6-v2)
   - Handles text chunking with overlap
   - Provides search functionality

4. **RAG Service** (`services/rag_service.py`)
   - Implements RAG pipeline
   - Retrieves relevant context from vector store
   - Integrates with Groq API or Hugging Face Inference API
   - Formats responses with source citations

### Frontend Components

1. **Main Page** (`app/page.tsx`)
   - Chat interface with message history
   - PDF upload functionality
   - URL input and scraping
   - Document list with delete functionality
   - Real-time chat with loading states

## 🔌 API Endpoints

- `GET /` - API status
- `GET /health` - Health check
- `POST /api/upload-pdf` - Upload and process PDF
- `POST /api/scrape-url` - Scrape URL content
- `POST /api/chat` - Chat with RAG
- `GET /api/documents` - List all documents
- `DELETE /api/documents/{doc_id}` - Delete a document

## 🗄️ Data Flow

1. **Upload/Scrape** → Extract text → Chunk text → Generate embeddings → Store in ChromaDB
2. **Query** → Generate query embedding → Search ChromaDB → Retrieve top chunks → Format context → Send to LLM → Return answer with sources

## 🔐 Environment Variables

### Backend (.env)
- `GROQ_API_KEY` - Groq API key for LLM
- `HUGGINGFACE_API_KEY` - Hugging Face API key (alternative)
- `USE_GROQ` - Boolean to choose LLM provider
- `CHROMA_DB_PATH` - Path to ChromaDB storage

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL` - Backend API URL

