from typing import List, Dict, Any, Optional
from app.services.llm_service import LLMService
from app.services.document_service import DocumentService
from sqlalchemy.orm import Session

class WorkflowExecutor:
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = LLMService()
        self.document_service = DocumentService()
    
    def execute_workflow(
        self,
        query: str,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute workflow based on node connections"""
        execution_log = []
        
        # Build node map for easy lookup
        node_map = {node["id"]: node for node in nodes}
        # Build forward edge map (source -> targets)
        forward_edges = {}
        for edge in edges:
            if edge["source"] not in forward_edges:
                forward_edges[edge["source"]] = []
            forward_edges[edge["source"]].append(edge["target"])
        
        # Find entry point (User Query component)
        user_query_node = None
        for node in nodes:
            if node.get("type") == "userQuery":
                user_query_node = node
                break
        
        if not user_query_node:
            raise ValueError("Workflow must contain a User Query component")
        
        # Traverse workflow
        current_data = {"query": query}
        visited = set()
        
        def process_node(node_id: str):
            if node_id in visited:
                return current_data
            
            visited.add(node_id)
            node = node_map[node_id]
            node_type = node.get("type")
            node_data = node.get("data", {})
            
            execution_log.append({
                "node_id": node_id,
                "node_type": node_type,
                "status": "processing"
            })
            
            result = None
            
            if node_type == "userQuery":
                result = current_data.get("query", "")
                execution_log[-1]["output"] = f"Query: {result}"
            
            elif node_type == "knowledgeBase":
                # Get configuration
                document_ids = node_data.get("document_ids", [])
                top_k = node_data.get("top_k", 5)
                
                # Search documents
                if current_data.get("query"):
                    search_results = self.document_service.search_documents(
                        self.db,
                        current_data["query"],
                        top_k=top_k
                    )
                    context = "\n".join([r["chunk_text"] for r in search_results])
                    result = context
                    execution_log[-1]["output"] = f"Retrieved {len(search_results)} relevant chunks"
                else:
                    result = ""
                    execution_log[-1]["output"] = "No query provided for knowledge base search"
            
            elif node_type == "webSearch":
                if current_data.get("query"):
                    web_results = self.llm_service._web_search(current_data["query"])
                    if web_results and web_results.get("results"):
                        context = "\n".join(
                            [r.get("snippet", "") for r in web_results.get("results", []) if r.get("snippet")]
                        )
                        result = context
                        execution_log[-1]["output"] = "Retrieved web search context"
                    else:
                        result = ""
                        execution_log[-1]["output"] = "No web search results found"
                else:
                    result = ""
                    execution_log[-1]["output"] = "No query provided for web search"

            elif node_type == "llmEngine":
                # Get configuration
                provider = node_data.get("provider")  # None means use default
                model = node_data.get("model")  # None means use default
                custom_prompt = node_data.get("custom_prompt")
                use_web_search = node_data.get("use_web_search", False)
                
                # Get query and context
                query_text = current_data.get("query", "")
                context = current_data.get("context", "")
                
                # If no context from knowledge base, try a direct search in current data
                if not context and "context" in current_data:
                    context = current_data["context"]
                
                print(f"[DEBUG] Executing LLM Engine. Context length: {len(context) if context else 0}")
                
                # Generate response
                llm_response = self.llm_service.generate_response(
                    query=query_text,
                    context=context,
                    provider=provider,
                    model=model,
                    custom_prompt=custom_prompt,
                    use_web_search=use_web_search
                )
                result = llm_response["response"]
                execution_log[-1]["output"] = f"Generated response using {provider or 'default'}"
            
            elif node_type == "output":
                result = current_data.get("response", current_data.get("query", ""))
                execution_log[-1]["output"] = "Prepared output"
            
            # Update current data based on node type
            if node_type == "knowledgeBase":
                current_data["context"] = result
            elif node_type == "webSearch":
                current_data["context"] = result
            elif node_type == "llmEngine":
                current_data["response"] = result
            elif node_type == "output":
                current_data["final_response"] = result
            
            execution_log[-1]["status"] = "completed"
            
            # Process connected nodes (forward traversal)
            if node_id in forward_edges:
                for next_node_id in forward_edges[node_id]:
                    process_node(next_node_id)
            
            return result
        
        # Start execution from user query node
        process_node(user_query_node["id"])
        
        final_response = current_data.get("final_response", current_data.get("response", "No response generated"))
        
        return {
            "response": final_response,
            "execution_log": execution_log
        }
