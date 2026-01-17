import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { toast } from 'react-hot-toast'
import CreateStackModal from './CreateStackModal'
import './Dashboard.css'

const API_BASE_URL = 'http://localhost:8001/api'

function Dashboard({ onSelectStack, onCreateNewStack, refreshKey }) {
  const [stacks, setStacks] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)

  useEffect(() => {
    fetchStacks()
  }, [refreshKey])

  const fetchStacks = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE_URL}/workflows`)
      setStacks(response.data)
    } catch (error) {
      console.error('Error fetching stacks:', error)
      toast.error('Failed to load stacks')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateStack = async (name, description) => {
    try {
      setShowCreateModal(false)
      onCreateNewStack(name, description)
    } catch (error) {
      console.error('Error creating stack:', error)
    }
  }

  const handleEditStack = (stack) => {
    onSelectStack(stack)
  }

  const handleDeleteStack = async (e, stackId) => {
    e.stopPropagation()
    if (!window.confirm('Are you sure you want to delete this stack?')) return

    try {
      await axios.delete(`${API_BASE_URL}/workflows/${stackId}`)
      toast.success('Stack deleted successfully')
      fetchStacks()
    } catch (error) {
      console.error('Error deleting stack:', error)
      toast.error('Failed to delete stack')
    }
  }

  return (
    <div className="dashboard">
      {/* Top Navbar */}
      <div className="dashboard-navbar">
        <div className="navbar-logo">
          <div className="navbar-logo-circle">
            <span>ai</span>
          </div>
          <span className="navbar-logo-name">GenAI Stack</span>
        </div>
        <div className="navbar-profile">S</div>
      </div>

      {/* Content Area */}
      <div className="dashboard-content">
        {/* Section Header */}
        <div className="section-header">
          <h1 className="section-title">My Stacks</h1>
          <button 
            className="new-stack-button"
            onClick={() => setShowCreateModal(true)}
          >
            + New Stack
          </button>
        </div>

        {/* Stacks Content */}
        {loading ? (
          <div className="loading-state">
            <p>Loading stacks...</p>
          </div>
        ) : stacks.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-card">
              <h2>Create New Stack</h2>
              <p>Start building your generative AI apps with our essential tools and frameworks</p>
              <button 
                className="new-stack-button"
                onClick={() => setShowCreateModal(true)}
              >
                + New Stack
              </button>
            </div>
          </div>
        ) : (
          <div className="stacks-grid">
            {stacks.map((stack) => (
              <div 
                key={stack.id} 
                className="stack-card"
                onClick={() => handleEditStack(stack)}
              >
                <div className="stack-card-content">
                  <div className="stack-card-header">
                    <h3 className="stack-card-title">{stack.name || 'Unnamed Stack'}</h3>
                    <button 
                      className="delete-stack-button"
                      onClick={(e) => handleDeleteStack(e, stack.id)}
                      title="Delete Stack"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M3 6h18"></path>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                      </svg>
                    </button>
                  </div>
                  <p className="stack-card-description">
                    {stack.description || 'No description'}
                  </p>
                </div>
                <div className="stack-card-footer">
                  <button 
                    className="edit-stack-button"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleEditStack(stack)
                    }}
                  >
                    Edit Stack
                    <svg className="external-link-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                      <polyline points="15 3 21 3 21 9"></polyline>
                      <line x1="10" y1="14" x2="21" y2="3"></line>
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {showCreateModal && (
        <CreateStackModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreateStack}
        />
      )}
    </div>
  )
}

export default Dashboard
