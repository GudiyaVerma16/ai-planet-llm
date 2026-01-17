import React, { useState } from 'react'
import './CreateStackModal.css'

function CreateStackModal({ onClose, onCreate }) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  const isValid = name.trim().length > 0

  const handleSubmit = (e) => {
    e.preventDefault()
    if (isValid) {
      onCreate(name.trim(), description.trim())
      setName('')
      setDescription('')
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Stack</h2>
          <button className="modal-close-button" onClick={onClose}>
            ×
          </button>
        </div>
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-field">
            <label htmlFor="stack-name">Name</label>
            <input
              id="stack-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter stack name"
              autoFocus
              required
            />
          </div>
          <div className="form-field">
            <label htmlFor="stack-description">Description</label>
            <textarea
              id="stack-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter stack description"
              rows={4}
            />
          </div>
          <div className="modal-actions">
            <button type="button" className="cancel-button" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="create-button" disabled={!isValid}>
              Create
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CreateStackModal
