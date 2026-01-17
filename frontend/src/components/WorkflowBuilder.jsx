import React, { useState, useCallback, useRef, useEffect } from 'react'
import ReactFlow, {
  Background,
  Controls,
  addEdge,
  useNodesState,
  useEdgesState,
  MarkerType,
  Handle,
  Position,
} from 'reactflow'
import 'reactflow/dist/style.css'
import ComponentLibrary from './ComponentLibrary'
import { toast } from 'react-hot-toast'
import axios from 'axios'
import './WorkflowBuilder.css'

const API_BASE_URL = 'http://localhost:8001/api'

// User Query Node
function UserQueryNode({ data, selected }) {
  return (
    <div className={`workflow-node user-query-node ${selected ? 'selected' : ''}`}>
      <div className="node-header">
        <span className="node-icon">📝</span>
        <span className="node-title">User Query</span>
        <span className="node-settings">⚙️</span>
      </div>
      <div className="node-description">Enter point for querys</div>
      <div className="node-fields">
        <div className="node-field">
          <label>User Query</label>
          <input
            type="text"
            value={data?.user_query || ''}
            onChange={(e) => data?.onDataChange?.({ user_query: e.target.value })}
            placeholder="Write your query here"
            className="node-input"
          />
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        id="query"
        className="handle-source handle-orange"
      />
      <div className="handle-label handle-label-bottom">Query</div>
    </div>
  )
}

// Knowledge Base Node
function KnowledgeBaseNode({ data, selected }) {
  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await axios.post(`${API_BASE_URL}/documents/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      data?.onDocumentUpload?.()
      const currentIds = data?.document_ids || []
      data?.onDataChange?.({ document_ids: [...currentIds, response.data.id] })
      toast.success('File uploaded successfully!')
    } catch (error) {
      console.error('Upload error:', error.response?.data || error)
      toast.error(
        error.response?.data?.detail ||
        (typeof error.response?.data === 'string' ? error.response.data : null) ||
        error.message ||
        'Error uploading file'
      )
    }
  }

  return (
    <div className={`workflow-node knowledge-base-node ${selected ? 'selected' : ''}`}>
      <Handle
        type="target"
        position={Position.Left}
        id="query"
        className="handle-target handle-orange"
      />
      <div className="handle-label handle-label-left">Query</div>
      
      <div className="node-header">
        <span className="node-icon">📋</span>
        <span className="node-title">Knowledge Base</span>
        <span className="node-settings">⚙️</span>
      </div>
      <div className="node-description">Let LLM search info in your file</div>
      <div className="node-fields">
        <div className="node-field">
          <label>File for Knowledge Base</label>
          <label className="upload-button">
            <input type="file" accept=".pdf" onChange={handleFileUpload} style={{ display: 'none' }} />
            Upload File <span className="upload-icon">↑</span>
          </label>
        </div>
        <div className="node-field">
          <label>Embedding Model</label>
          <select
            value={data?.embedding_model || 'text-embedding-3-large'}
            onChange={(e) => data?.onDataChange?.({ embedding_model: e.target.value })}
            className="node-select"
          >
            <option value="text-embedding-3-large">text-embedding-3-large</option>
            <option value="text-embedding-3-small">text-embedding-3-small</option>
            <option value="text-embedding-ada-002">text-embedding-ada-002</option>
          </select>
        </div>
        <div className="node-field">
          <label>API Key</label>
          <div className="input-with-icon">
            <input
              type="password"
              value={data?.api_key || ''}
              onChange={(e) => data?.onDataChange?.({ api_key: e.target.value })}
              placeholder="••••••••••••••••"
              className="node-input"
            />
            <span className="eye-icon">👁</span>
          </div>
        </div>
      </div>
      
      <Handle
        type="source"
        position={Position.Right}
        id="context"
        className="handle-source handle-orange"
      />
      <div className="handle-label handle-label-right">Context</div>
    </div>
  )
}

// LLM Engine Node
function LLMEngineNode({ data, selected }) {
  return (
    <div className={`workflow-node llm-engine-node ${selected ? 'selected' : ''}`}>
      <Handle
        type="target"
        position={Position.Left}
        id="context"
        className="handle-target handle-blue"
      />
      
      <div className="node-header">
        <span className="node-icon">✨</span>
        <span className="node-title">LLM Engine</span>
        <span className="node-settings">⚙️</span>
      </div>
      <div className="node-description">Run a query with LLM (OpenAI or Gemini)</div>
      <div className="node-fields">
        <div className="node-field">
          <label>Provider</label>
          <select
            value={data?.provider || 'gemini'}
            onChange={(e) => {
              const provider = e.target.value
              const defaultModel = provider === 'gemini' ? 'gemini-2.0-flash' : 'gpt-3.5-turbo'
              data?.onDataChange?.({ provider, model: data?.model || defaultModel })
            }}
            className="node-select"
          >
            <option value="gemini">Google Gemini</option>
            <option value="openai">OpenAI</option>
          </select>
        </div>
        <div className="node-field">
          <label>Model</label>
          <select
            value={data?.model || (data?.provider === 'openai' ? 'gpt-3.5-turbo' : 'gemini-2.0-flash')}
            onChange={(e) => data?.onDataChange?.({ model: e.target.value })}
            className="node-select"
          >
            {data?.provider === 'openai' ? (
              <>
                <option value="gpt-4o-mini">GPT 4o- Mini</option>
                <option value="gpt-4-turbo">GPT 4 Turbo</option>
                <option value="gpt-4">GPT 4</option>
                <option value="gpt-3.5-turbo">GPT 3.5 Turbo</option>
              </>
            ) : (
              <>
                <option value="gemini-2.0-flash">Gemini 2.0 Flash (Recommended)</option>
                <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                <option value="gemini-1.5-flash">Gemini 1.5 Flash (Legacy)</option>
                <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                <option value="gemini-pro">Gemini Pro (Legacy)</option>
              </>
            )}
          </select>
        </div>
        <div className="node-field">
          <label>API Key</label>
          <div className="input-with-icon">
            <input
              type="password"
              value={data?.api_key || ''}
              onChange={(e) => data?.onDataChange?.({ api_key: e.target.value })}
              placeholder="••••••••••••••••"
              className="node-input"
            />
            <span className="eye-icon">👁</span>
          </div>
        </div>
        <div className="node-field">
          <label>Prompt</label>
          <textarea
            value={data?.custom_prompt || 'You are a helpful PDF assistant. Use web search if the PDF lacks context\nCONTEXT: {context}\nUser Query: {query}'}
            onChange={(e) => data?.onDataChange?.({ custom_prompt: e.target.value })}
            className="node-textarea"
            rows={4}
          />
        </div>
        <div className="node-field">
          <label>Temperature</label>
          <input
            type="number"
            value={data?.temperature || 0.75}
            onChange={(e) => data?.onDataChange?.({ temperature: parseFloat(e.target.value) })}
            min="0"
            max="2"
            step="0.01"
            className="node-input"
          />
        </div>
        <div className="node-field toggle-field">
          <label>WebSearch Tool</label>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={data?.use_web_search || false}
              onChange={(e) => data?.onDataChange?.({ use_web_search: e.target.checked })}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
        {data?.use_web_search && (
          <div className="node-field">
            <label>SERF API</label>
            <div className="input-with-icon">
              <input
                type="password"
                value={data?.serpapi_key || ''}
                onChange={(e) => data?.onDataChange?.({ serpapi_key: e.target.value })}
                placeholder="••••••••••••••••"
                className="node-input"
              />
              <span className="eye-icon">👁</span>
            </div>
          </div>
        )}
      </div>
      
      <Handle
        type="source"
        position={Position.Bottom}
        id="output"
        className="handle-source handle-blue"
      />
      <div className="handle-label handle-label-bottom">Output</div>
    </div>
  )
}

// Output Node
function OutputNode({ data, selected }) {
  return (
    <div className={`workflow-node output-node ${selected ? 'selected' : ''}`}>
      <Handle
        type="target"
        position={Position.Left}
        id="output"
        className="handle-target handle-green"
      />
      <div className="handle-label handle-label-left">Output</div>
      
      <div className="node-header">
        <span className="node-icon">↩️</span>
        <span className="node-title">Output</span>
        <span className="node-settings">⚙️</span>
      </div>
      <div className="node-description">Output of the result nodes as text</div>
      <div className="node-fields">
        <div className="node-field">
          <label>Output Text</label>
          <textarea
            value={data?.output_text || ''}
            placeholder="Output will be generated based on query"
            className="node-textarea"
            rows={3}
            readOnly
          />
        </div>
      </div>
    </div>
  )
}

const nodeTypes = {
  userQuery: UserQueryNode,
  knowledgeBase: KnowledgeBaseNode,
  llmEngine: LLMEngineNode,
  output: OutputNode,
}

function WorkflowBuilder({ onWorkflowBuilt, currentWorkflow, initialName, initialDescription }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [selectedNode, setSelectedNode] = useState(null)
  const [componentTypes, setComponentTypes] = useState([])
  const [documents, setDocuments] = useState([])
  const reactFlowWrapper = useRef(null)
  const [reactFlowInstance, setReactFlowInstance] = useState(null)
  const [stackName, setStackName] = useState(initialName || currentWorkflow?.name || '')
  const [stackDescription, setStackDescription] = useState(initialDescription || currentWorkflow?.description || '')
  const [draggedType, setDraggedType] = useState(null)

  useEffect(() => {
    fetchComponentTypes()
    fetchDocuments()
    if (currentWorkflow) {
      setNodes(currentWorkflow.nodes || [])
      setEdges(currentWorkflow.edges || [])
    }
  }, [currentWorkflow])

  const fetchComponentTypes = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/components/types`)
      setComponentTypes(response.data.components)
    } catch (error) {
      console.error('Error fetching component types:', error)
    }
  }

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/documents`)
      setDocuments(response.data)
    } catch (error) {
      console.error('Error fetching documents:', error)
    }
  }

  const onConnect = useCallback(
    (params) => {
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            type: 'smoothstep',
            animated: false,
            style: { stroke: '#94a3b8', strokeWidth: 2 },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: '#94a3b8',
            },
          },
          eds
        )
      )
    },
    [setEdges]
  )

  const onDragStart = useCallback((event, nodeType) => {
    setDraggedType(nodeType)
    event.dataTransfer.setData('application/reactflow', nodeType)
    event.dataTransfer.setData('text/plain', nodeType)
    event.dataTransfer.effectAllowed = 'move'
  }, [])

  const handleComponentClick = useCallback((nodeType) => {
    const nodeWidth = 320
    const nodeHeight = 300
    const padding = 24
    const gapX = 32
    const gapY = 32

    const bounds = reactFlowWrapper.current?.getBoundingClientRect()
    const canvasLeft = bounds ? bounds.left : 0
    const canvasTop = bounds ? bounds.top : 0
    const canvasWidth = bounds ? bounds.width : window.innerWidth
    const canvasHeight = bounds ? bounds.height : window.innerHeight

    const basePosition = reactFlowInstance
      ? reactFlowInstance.screenToFlowPosition({
          x: canvasLeft + padding,
          y: canvasTop + padding,
        })
      : { x: padding, y: padding }

    const maxCols = Math.max(
      1,
      Math.floor((canvasWidth - padding * 2 + gapX) / (nodeWidth + gapX))
    )
    const maxRows = Math.max(
      1,
      Math.floor((canvasHeight - padding * 2 + gapY) / (nodeHeight + gapY))
    )

    const isOverlapping = (x, y, nodes) => {
      return nodes.some((n) => {
        const nx = n.position?.x ?? 0
        const ny = n.position?.y ?? 0
        const overlapX = Math.abs(nx - x) < nodeWidth
        const overlapY = Math.abs(ny - y) < nodeHeight
        return overlapX && overlapY
      })
    }

    setNodes((nds) => {
      let position = { x: basePosition.x, y: basePosition.y }
      let placed = false

      for (let row = 0; row < maxRows && !placed; row++) {
        for (let col = 0; col < maxCols && !placed; col++) {
          const x = basePosition.x + col * (nodeWidth + gapX)
          const y = basePosition.y + row * (nodeHeight + gapY)
          if (!isOverlapping(x, y, nds)) {
            position = { x, y }
            placed = true
          }
        }
      }

      if (!placed) {
        const x = basePosition.x + (nds.length % maxCols) * (nodeWidth + gapX)
        const y = basePosition.y + Math.floor(nds.length / maxCols) * (nodeHeight + gapY)
        position = { x, y }
      }

      const newNode = {
        id: `${nodeType}-${Date.now()}`,
        type: nodeType,
        position,
        data: { label: nodeType },
      }
      return nds.concat(newNode)
    })
  }, [reactFlowInstance, setNodes])

  const onDragOver = useCallback((event) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback(
    (event) => {
      event.preventDefault()
      event.stopPropagation()

      let type = event.dataTransfer.getData('application/reactflow')
      if (!type) {
        type = event.dataTransfer.getData('text/plain')
      }
      if (!type) {
        type = draggedType
      }

      if (!type || !reactFlowInstance) {
        return
      }

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      })

      const newNode = {
        id: `${type}-${Date.now()}`,
        type,
        position,
        data: { label: type },
      }

      setNodes((nds) => nds.concat(newNode))
      setDraggedType(null)
    },
    [reactFlowInstance, setNodes, draggedType]
  )

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node)
  }, [])

  const onPaneClick = useCallback(() => {
    setSelectedNode(null)
  }, [])

  const handleNodeDataChange = useCallback((nodeId, newData) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId ? { ...node, data: { ...node.data, ...newData } } : node
      )
    )
  }, [setNodes])

  const validateWorkflow = () => {
    if (nodes.length === 0) {
      toast.error('Please add at least one component to the workflow')
      return false
    }
    const userQueryNodes = nodes.filter((n) => n.type === 'userQuery')
    if (userQueryNodes.length === 0) {
      toast.error('Workflow must contain a User Query component')
      return false
    }
    const outputNodes = nodes.filter((n) => n.type === 'output')
    if (outputNodes.length === 0) {
      toast.error('Workflow must contain an Output component')
      return false
    }
    return true
  }

  const handleBuildStack = async () => {
    if (!validateWorkflow()) return

    try {
      const workflowData = {
        name: stackName || 'Unnamed Stack',
        description: stackDescription || '',
        nodes: nodes.map((node) => ({
          id: node.id,
          type: node.type,
          position: node.position,
          data: node.data,
        })),
        edges: edges.map((edge) => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          sourceHandle: edge.sourceHandle,
          targetHandle: edge.targetHandle,
        })),
      }

      let response
      if (currentWorkflow?.id) {
        response = await axios.put(`${API_BASE_URL}/workflows/${currentWorkflow.id}`, workflowData)
        toast.success('Stack updated successfully!')
      } else {
        response = await axios.post(`${API_BASE_URL}/workflows`, workflowData)
        toast.success('Stack created successfully!')
      }

      onWorkflowBuilt({
        id: response.data.id,
        name: response.data.name,
        description: response.data.description,
        ...workflowData,
      })
    } catch (error) {
      toast.error('Error saving stack: ' + (error.response?.data?.detail || error.message))
    }
  }

  // Listen for save event from header
  useEffect(() => {
    const handleSaveEvent = () => handleBuildStack()
    window.addEventListener('saveWorkflow', handleSaveEvent)
    return () => window.removeEventListener('saveWorkflow', handleSaveEvent)
  }, [nodes, edges, stackName, stackDescription, currentWorkflow])

  return (
    <div className="workflow-builder">
      {/* Left Sidebar */}
      <ComponentLibrary
        componentTypes={componentTypes}
        onDragStart={onDragStart}
        onDocumentUpload={fetchDocuments}
        onComponentClick={handleComponentClick}
      />
      
      {/* Main Canvas */}
      <div className="workflow-canvas" ref={reactFlowWrapper}>
        {nodes.length === 0 && (
          <div className="empty-canvas-state">
            <div className="empty-canvas-icon-wrapper">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth="1.5">
                <rect x="3" y="3" width="18" height="18" rx="2" strokeDasharray="3 3"/>
                <path d="M12 8v8M8 12h8" stroke="#22c55e" strokeWidth="2"/>
              </svg>
            </div>
            <p className="empty-canvas-text">Drag & drop to get started</p>
          </div>
        )}
        <ReactFlow
          nodes={nodes.map(node => ({
            ...node,
            data: {
              ...node.data,
              onDataChange: (newData) => handleNodeDataChange(node.id, newData),
              documents: documents,
              onDocumentUpload: fetchDocuments,
            }
          }))}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={setReactFlowInstance}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodeTypes={nodeTypes}
          fitView
        >
          <Background color="#e5e5e5" gap={20} size={1} />
          <Controls />
        </ReactFlow>
        
        {/* Build Stack Button */}
        <div className="build-stack-container">
          <span className="build-stack-label">Build Stack</span>
          <button className="build-stack-button" onClick={handleBuildStack}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}

export default WorkflowBuilder
