# RAG Document Bot

A full-stack Retrieval-Augmented Generation (RAG) system with a Python FastAPI backend and React frontend. Upload documents, ask questions, and get AI-powered answers based on your document content.

## Features

- **Document Upload**: Support for PDF, DOCX, and TXT files
- **Text Extraction & Chunking**: Automatic text extraction and intelligent chunking
- **Vector Search**: FAISS-based similarity search using OpenAI embeddings
- **AI-Powered Q&A**: Get contextual answers using GPT-3.5-turbo
- **Modern UI**: Clean, responsive interface built with React and Tailwind CSS
- **Document Management**: View, manage, and delete uploaded documents

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **OpenAI**: Text embeddings and GPT-3.5-turbo for Q&A
- **FAISS**: Vector similarity search
- **LangChain**: Text chunking and processing
- **PyPDF2 & python-docx**: Document text extraction

### Frontend
- **React**: UI framework
- **Tailwind CSS**: Styling
- **Axios**: HTTP client
- **Vite**: Build tool

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key

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

4. Create environment file:
```bash
cp env.example .env
```

5. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

6. Run the backend server:
```bash
python main.py
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

### POST /upload-document
Upload and process a document.

**Request**: Multipart form data with file
**Response**: Document metadata including ID and chunk count

### POST /ask
Ask a question about uploaded documents.

**Request**: JSON with query string
**Response**: AI-generated answer with source citations

### GET /documents
Get list of uploaded documents.

**Response**: Array of document metadata

### DELETE /documents/{id}
Delete a document and its vectors.

**Response**: Success confirmation

## Usage

1. **Upload Documents**: Use the file upload area to add PDF, DOCX, or TXT files
2. **Ask Questions**: Type questions in the chat interface
3. **View Sources**: Each answer includes relevant document chunks as sources
4. **Manage Documents**: Switch to the Documents tab to view and delete files

## Project Structure

```
rag-doc-bot/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── embedding.py         # OpenAI embedding management
│   ├── vector_store.py      # FAISS vector store operations
│   ├── document_handler.py  # Document processing and chunking
│   ├── requirements.txt     # Python dependencies
│   └── env.example         # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── FileUpload.jsx
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── DocumentList.jsx
│   │   │   └── Notification.jsx
│   │   ├── api/            # API service functions
│   │   │   └── api.js
│   │   ├── App.jsx         # Main application component
│   │   └── index.css       # Global styles
│   ├── package.json        # Node.js dependencies
│   └── tailwind.config.js  # Tailwind configuration
└── README.md
```

## Environment Variables

### Backend (.env)
- `OPENAI_API_KEY`: Your OpenAI API key

## Development

### Backend Development
- The backend uses FastAPI with automatic API documentation
- Visit `http://localhost:8000/docs` for interactive API docs
- CORS is configured for frontend development

### Frontend Development
- Hot reload enabled with Vite
- Tailwind CSS for styling
- Component-based architecture

## Troubleshooting

### Common Issues

1. **OpenAI API Key**: Ensure your API key is valid and has sufficient credits
2. **CORS Errors**: Backend CORS is configured for localhost:5173
3. **File Upload Issues**: Check file size (10MB limit) and supported formats
4. **Vector Store**: FAISS index files are stored locally in the backend directory

### Performance Tips

- Large documents are automatically chunked for better search
- Embeddings are cached in the FAISS index
- Consider using GPU-accelerated FAISS for production

## License

MIT License - feel free to use this project for your own applications! 