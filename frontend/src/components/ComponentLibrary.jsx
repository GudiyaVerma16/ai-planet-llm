import React from 'react'
import './ComponentLibrary.css'

function ComponentLibrary({ componentTypes, onDragStart, onDocumentUpload, onComponentClick }) {
  
  const getComponentIcon = (type) => {
    const icons = {
      userQuery: '📝',
      llmEngine: '✨',
      knowledgeBase: '📋',
      output: '↩️',
    }
    return icons[type] || '📦'
  }

  const getComponentLabel = (type, defaultName) => {
    const labels = {
      userQuery: 'User Query',
      llmEngine: 'LLM (OpenAI)',
      knowledgeBase: 'Knowledge Base',
      output: 'Output',
    }
    return labels[type] || defaultName
  }

  // Show 4 components in order
  const filteredComponents = [...componentTypes]
    .filter(c => ['userQuery', 'llmEngine', 'knowledgeBase', 'output'].includes(c.type))
    .sort((a, b) => {
      const order = { userQuery: 1, llmEngine: 2, knowledgeBase: 3, output: 4 }
      return (order[a.type] || 99) - (order[b.type] || 99)
    })

  return (
    <div className="sidebar">
      {/* Chat With AI Header */}
      <div className="sidebar-header">
        <span className="sidebar-title">Chat With AI</span>
        <svg className="sidebar-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
          <polyline points="15 3 21 3 21 9"></polyline>
          <line x1="10" y1="14" x2="21" y2="3"></line>
        </svg>
      </div>

      {/* Components Section */}
      <div className="sidebar-section">
        <h3 className="sidebar-section-title">Components</h3>
        
        <div className="component-list">
          {filteredComponents.map((component) => (
            <div
              key={component.type}
              className="component-item"
              draggable
              onDragStart={(e) => onDragStart?.(e, component.type)}
              onClick={() => onComponentClick?.(component.type)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  onComponentClick?.(component.type)
                }
              }}
            >
              <span className="component-icon">{getComponentIcon(component.type)}</span>
              <span className="component-name">
                {getComponentLabel(component.type, component.name)}
              </span>
              <span className="component-drag-handle">≡</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ComponentLibrary
