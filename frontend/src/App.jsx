import { useState } from 'react'
import FileUpload from './components/FileUpload'
import ChatInterface from './components/ChatInterface'
import DocumentList from './components/DocumentList'
import Notification from './components/Notification'
import './App.css'

function App() {
  const [notifications, setNotifications] = useState([])
  const [activeTab, setActiveTab] = useState('chat')

  const addNotification = (message, type = 'success') => {
    const id = Date.now()
    setNotifications(prev => [...prev, { id, message, type }])
  }

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id))
  }

  const handleUploadSuccess = (result) => {
    addNotification(`Document "${result.filename}" uploaded successfully!`)
  }

  const handleUploadError = (error) => {
    addNotification(error, 'error')
  }

  const handleDocumentDeleted = () => {
    addNotification('Document deleted successfully')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="text-2xl">🤖</div>
              <h1 className="text-xl font-bold text-gray-900">RAG Document Bot</h1>
            </div>
            <div className="text-sm text-gray-500">
              Powered by OpenAI & FAISS
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 h-[calc(100vh-8rem)]">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border h-full flex flex-col">
              {/* Tab Navigation */}
              <div className="border-b flex-shrink-0">
                <nav className="flex">
                  <button
                    onClick={() => setActiveTab('chat')}
                    className={`flex-1 px-4 py-3 text-sm font-medium ${
                      activeTab === 'chat'
                        ? 'text-blue-600 border-b-2 border-blue-600'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    💬 Upload
                  </button>
                  <button
                    onClick={() => setActiveTab('documents')}
                    className={`flex-1 px-4 py-3 text-sm font-medium ${
                      activeTab === 'documents'
                        ? 'text-blue-600 border-b-2 border-blue-600'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    📚 Documents
                  </button>
                </nav>
              </div>

              {/* Tab Content */}
              <div className="flex-1 overflow-y-auto">
                {activeTab === 'chat' ? (
                  <div className="p-4">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">
                      Upload Documents
                    </h3>
                    <FileUpload
                      onUploadSuccess={handleUploadSuccess}
                      onUploadError={handleUploadError}
                    />
                  </div>
                ) : (
                  <DocumentList onDocumentDeleted={handleDocumentDeleted} />
                )}
              </div>
            </div>
          </div>

          {/* Main Chat Area */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow-sm border h-full">
              <ChatInterface />
            </div>
          </div>
        </div>
      </div>

      {/* Notifications */}
      {notifications.map((notification) => (
        <Notification
          key={notification.id}
          message={notification.message}
          type={notification.type}
          onClose={() => removeNotification(notification.id)}
        />
      ))}
    </div>
  );
}

export default App;