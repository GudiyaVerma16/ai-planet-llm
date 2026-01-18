import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { toast } from 'react-hot-toast'
import { API_BASE_URL } from '../config'
import './ChatInterface.css'

function ChatInterface({ workflow, onClose }) {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage = {
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/chat/query`, {
        workflow_id: workflow.id,
        query: inputValue,
        nodes: workflow.nodes,
        edges: workflow.edges,
      })

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        execution_log: response.data.execution_log,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      toast.error('Error processing query: ' + (error.response?.data?.detail || error.message))
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your query.',
        isError: true,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="chat-overlay" onClick={onClose}>
      <div className="chat-interface" onClick={(e) => e.stopPropagation()}>
        <div className="chat-header">
          <div className="chat-header-content">
            <div className="chat-logo">
              <div className="logo-circle-small">
                <span className="logo-text-small">ai</span>
              </div>
              <h3>GenAI Stack Chat</h3>
            </div>
            <button className="chat-close-button" onClick={onClose}>
              ×
            </button>
          </div>
          <p className="chat-subtitle">Start a conversation to test your stack</p>
        </div>
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="empty-chat">
              <p>Start a conversation to test your stack</p>
            </div>
          )}
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                {message.execution_log && (
                  <details className="execution-log">
                    <summary>Execution Log</summary>
                    <pre>{JSON.stringify(message.execution_log, null, 2)}</pre>
                  </details>
                )}
                <div className="message-timestamp">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message assistant">
              <div className="message-content">
                <div className="loading-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <div className="chat-input-container">
          <textarea
            className="chat-input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Send a message"
            rows={2}
          />
          <button
            className="send-button"
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
          >
            <span className="send-icon">✈</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface
