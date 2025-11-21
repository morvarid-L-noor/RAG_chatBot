'use client'

import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { Upload, Link as LinkIcon, Send, FileText, Trash2, Loader2 } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
}

interface Document {
  doc_id: string
  source: string
  type: string
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [urlLoading, setUrlLoading] = useState(false)
  const [urlInput, setUrlInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchDocuments()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/documents`)
      if (response.data.success) {
        setDocuments(response.data.documents)
      }
    } catch (error) {
      console.error('Error fetching documents:', error)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(`${API_URL}/api/upload-pdf`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      if (response.data.success) {
        alert(`PDF uploaded successfully! Processed ${response.data.text_length} characters.`)
        fetchDocuments()
      }
    } catch (error: any) {
      alert(`Error uploading PDF: ${error.response?.data?.error || error.message}`)
    } finally {
      setUploading(false)
      e.target.value = '' // Reset input
    }
  }

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!urlInput.trim()) return

    setUrlLoading(true)
    try {
      const response = await axios.post(`${API_URL}/api/scrape-url`, {
        url: urlInput.trim(),
      })

      if (response.data.success) {
        alert(`URL scraped successfully! Processed ${response.data.text_length} characters.`)
        setUrlInput('')
        fetchDocuments()
      }
    } catch (error: any) {
      alert(`Error scraping URL: ${error.response?.data?.error || error.message}`)
    } finally {
      setUrlLoading(false)
    }
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await axios.post(`${API_URL}/api/chat`, {
        message: userMessage.content,
        session_id: sessionId,
      })

      if (response.data.success) {
        if (!sessionId && response.data.session_id) {
          setSessionId(response.data.session_id)
        }

        const assistantMessage: Message = {
          role: 'assistant',
          content: response.data.response,
          sources: response.data.sources,
        }

        setMessages((prev) => [...prev, assistantMessage])
      }
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `Error: ${error.response?.data?.error || error.message}`,
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteDocument = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    try {
      const response = await axios.delete(`${API_URL}/api/documents/${docId}`)
      if (response.data.success) {
        fetchDocuments()
        alert('Document deleted successfully')
      }
    } catch (error: any) {
      alert(`Error deleting document: ${error.response?.data?.error || error.message}`)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="bg-white rounded-lg shadow-xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6">
            <h1 className="text-3xl font-bold mb-2">RAG Knowledge Chatbot</h1>
            <p className="text-blue-100">Upload PDFs or paste URLs to build your knowledge base</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
            {/* Left Sidebar - Upload & Documents */}
            <div className="lg:col-span-1 space-y-4">
              {/* Upload Section */}
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <h2 className="text-lg font-semibold mb-4 text-gray-800">Add Knowledge</h2>
                
                {/* PDF Upload */}
                <div className="mb-4">
                  <label className="block mb-2 text-sm font-medium text-gray-700">
                    Upload PDF
                  </label>
                  <div className="relative">
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={handleFileUpload}
                      className="hidden"
                      id="pdf-upload"
                      disabled={uploading}
                    />
                    <label
                      htmlFor="pdf-upload"
                      className={`flex items-center justify-center px-4 py-2 border-2 border-dashed rounded-lg cursor-pointer transition-colors ${
                        uploading
                          ? 'border-gray-300 bg-gray-100 cursor-not-allowed'
                          : 'border-blue-300 hover:border-blue-500 hover:bg-blue-50'
                      }`}
                    >
                      {uploading ? (
                        <>
                          <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                          <span className="text-sm text-gray-600">Uploading...</span>
                        </>
                      ) : (
                        <>
                          <Upload className="w-5 h-5 mr-2 text-blue-600" />
                          <span className="text-sm text-gray-700">Choose PDF</span>
                        </>
                      )}
                    </label>
                  </div>
                </div>

                {/* URL Input */}
                <div>
                  <label className="block mb-2 text-sm font-medium text-gray-700">
                    Paste URL
                  </label>
                  <form onSubmit={handleUrlSubmit} className="flex gap-2">
                    <input
                      type="url"
                      value={urlInput}
                      onChange={(e) => setUrlInput(e.target.value)}
                      placeholder="https://example.com"
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      disabled={urlLoading}
                    />
                    <button
                      type="submit"
                      disabled={urlLoading || !urlInput.trim()}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {urlLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <LinkIcon className="w-4 h-4" />
                      )}
                    </button>
                  </form>
                </div>
              </div>

              {/* Documents List */}
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <h2 className="text-lg font-semibold mb-4 text-gray-800">
                  Documents ({documents.length})
                </h2>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {documents.length === 0 ? (
                    <p className="text-sm text-gray-500 text-center py-4">
                      No documents yet. Upload a PDF or add a URL to get started.
                    </p>
                  ) : (
                    documents.map((doc) => (
                      <div
                        key={doc.doc_id}
                        className="flex items-center justify-between p-2 bg-white rounded border border-gray-200 hover:bg-gray-50"
                      >
                        <div className="flex items-center flex-1 min-w-0">
                          {doc.type === 'pdf' ? (
                            <FileText className="w-4 h-4 mr-2 text-blue-600 flex-shrink-0" />
                          ) : (
                            <LinkIcon className="w-4 h-4 mr-2 text-green-600 flex-shrink-0" />
                          )}
                          <span className="text-sm text-gray-700 truncate">{doc.source}</span>
                        </div>
                        <button
                          onClick={() => handleDeleteDocument(doc.doc_id)}
                          className="ml-2 p-1 text-red-600 hover:text-red-800 transition-colors"
                          title="Delete document"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            {/* Right Side - Chat */}
            <div className="lg:col-span-2 flex flex-col bg-white rounded-lg border border-gray-200">
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4 min-h-[400px] max-h-[600px]">
                {messages.length === 0 ? (
                  <div className="text-center text-gray-500 mt-20">
                    <p className="text-lg mb-2">👋 Welcome!</p>
                    <p>Start by uploading a PDF or adding a URL, then ask questions about the content.</p>
                  </div>
                ) : (
                  messages.map((message, idx) => (
                    <div
                      key={idx}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-4 ${
                          message.role === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        <p className="whitespace-pre-wrap">{message.content}</p>
                        {message.sources && message.sources.length > 0 && (
                          <div className="mt-2 pt-2 border-t border-gray-300">
                            <p className="text-xs font-semibold mb-1">Sources:</p>
                            <ul className="text-xs space-y-1">
                              {message.sources.map((source, i) => (
                                <li key={i} className="truncate">• {source}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 rounded-lg p-4">
                      <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <form onSubmit={handleSendMessage} className="border-t border-gray-200 p-4">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask a question about your documents..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={loading}
                  />
                  <button
                    type="submit"
                    disabled={loading || !input.trim()}
                    className={`px-6 py-2 text-white rounded-lg transition-all duration-200 flex items-center gap-2 font-medium ${
                      input.trim() && !loading
                        ? 'bg-blue-500 hover:bg-blue-600 shadow-lg shadow-blue-500/50 hover:shadow-blue-600/50 transform hover:scale-105'
                        : 'bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed'
                    }`}
                  >
                    {loading ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <>
                        <Send className="w-5 h-5" />
                        <span>Send</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

