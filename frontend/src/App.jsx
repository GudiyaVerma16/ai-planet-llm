import React, { useState, useCallback } from 'react'
import { Toaster } from 'react-hot-toast'
import Dashboard from './components/Dashboard'
import WorkflowBuilder from './components/WorkflowBuilder'
import ChatInterface from './components/ChatInterface'
import './App.css'

function App() {
  const [currentView, setCurrentView] = useState('dashboard') // 'dashboard' or 'workflow'
  const [currentWorkflow, setCurrentWorkflow] = useState(null)
  const [showChat, setShowChat] = useState(false)
  const [stackName, setStackName] = useState('')
  const [stackDescription, setStackDescription] = useState('')
  const [refreshDashboard, setRefreshDashboard] = useState(0)

  const handleSelectStack = useCallback((workflow) => {
    setCurrentWorkflow(workflow)
    setCurrentView('workflow')
  }, [])

  const handleCreateNewStack = useCallback((name, description) => {
    setStackName(name)
    setStackDescription(description)
    setCurrentWorkflow(null)
    setCurrentView('workflow')
  }, [])

  const handleWorkflowBuilt = useCallback((workflow) => {
    // Keep the saved workflow so user can chat with it
    setCurrentWorkflow(workflow)
    setStackName('')
    setStackDescription('')
    // Trigger dashboard refresh for when user goes back
    setRefreshDashboard(prev => prev + 1)
  }, [])

  const handleBackToDashboard = () => {
    setCurrentView('dashboard')
    setCurrentWorkflow(null)
    setShowChat(false)
    setStackName('')
    setStackDescription('')
  }

  return (
    <div className="app">
      <Toaster position="top-right" />
      {currentView === 'dashboard' ? (
        <Dashboard 
          onSelectStack={handleSelectStack}
          onCreateNewStack={handleCreateNewStack}
          refreshKey={refreshDashboard}
        />
      ) : (
        <>
          <header className="app-header">
            <div className="header-left">
              <button className="back-button" onClick={handleBackToDashboard}>
                ← Back
              </button>
              <div className="logo">
                <div className="logo-circle">
                  <span className="logo-text">ai</span>
                </div>
                <span className="logo-name">GenAI Stack</span>
              </div>
            </div>
            <div className="header-right">
              <button 
                className="save-button"
                onClick={() => {
                  const event = new Event('saveWorkflow')
                  window.dispatchEvent(event)
                }}
                title="Save Stack"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                  <polyline points="17 21 17 13 7 13 7 21"></polyline>
                  <polyline points="7 3 7 8 15 8"></polyline>
                </svg>
                Save
              </button>
              <div className="profile-icon">S</div>
            </div>
          </header>
          <div className="app-content">
            <WorkflowBuilder 
              onWorkflowBuilt={handleWorkflowBuilt}
              currentWorkflow={currentWorkflow}
              initialName={stackName}
              initialDescription={stackDescription}
            />
            {/* Chat FAB - Always visible, shows chat when workflow is saved */}
            <button 
              className="chat-fab"
              onClick={() => {
                if (currentWorkflow) {
                  setShowChat(true)
                } else {
                  // If no workflow saved yet, trigger save first
                  const event = new Event('saveWorkflow')
                  window.dispatchEvent(event)
                }
              }}
              title={currentWorkflow ? "Chat with Stack" : "Build Stack first to chat"}
            >
              <span className="chat-fab-icon">💬</span>
            </button>
            {showChat && currentWorkflow && (
              <ChatInterface workflow={currentWorkflow} onClose={() => setShowChat(false)} />
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default App
