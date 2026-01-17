import os
import time
from typing import Optional, Dict, Any
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=self.openai_api_key) if self.openai_api_key else None
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
        # Default provider: Google if available, else OpenAI
        if self.google_api_key:
            self.default_provider = "gemini"
        elif self.openai_api_key:
            self.default_provider = "openai"
        else:
            self.default_provider = "openai"
    
    def generate_response(
        self,
        query: str,
        context: Optional[str] = None,
        provider: str = None,
        model: str = None,
        custom_prompt: Optional[str] = None,
        use_web_search: bool = False
    ) -> Dict[str, Any]:
        # Use default provider if not specified
        if provider is None:
            provider = self.default_provider
        # Use default model if not specified
        if model is None:
            if provider == "gemini":
                model = "gemini-2.0-flash"  # Default to available model
            else:
                model = "gpt-3.5-turbo"
        """Generate response using LLM with optional context and web search"""
        web_results = None
        if use_web_search:
            web_results = self._web_search(query)
        
        # Build prompt
        prompt = self._build_prompt(query, context, custom_prompt, web_results)
        
        if provider == "openai":
            response = self._generate_openai_response(prompt, model)
        elif provider == "gemini":
            response = self._generate_gemini_response(prompt, model)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        
        return {
            "response": response,
            "web_results": web_results
        }
    
    def _build_prompt(
        self,
        query: str,
        context: Optional[str],
        custom_prompt: Optional[str],
        web_results: Optional[Dict]
    ) -> str:
        """Build the final prompt for LLM with smart tag replacement"""
        actual_context = context if context else "No relevant context found in file."
        
        if custom_prompt:
            # Smart replacement of {context} and {query} tags
            p = custom_prompt
            if "{context}" in p:
                p = p.replace("{context}", actual_context)
            else:
                p = f"{p}\n\nCONTEXT FROM FILE:\n{actual_context}"
                
            if "{query}" in p:
                p = p.replace("{query}", query)
            else:
                p = f"{p}\n\nUSER QUERY: {query}"
            
            if web_results and "{web_results}" in p:
                p = p.replace("{web_results}", str(web_results))
                
            return p
        
        # Default prompt if none provided
        return f"Answer based on context.\n\nCONTEXT:\n{actual_context}\n\nQUERY: {query}"
    
    def _generate_openai_response(self, prompt: str, model: str) -> str:
        """Generate response using OpenAI"""
        try:
            if not self.openai_api_key or not self.openai_client:
                raise ValueError("OPENAI_API_KEY is missing. Please set it in backend/.env")
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating OpenAI response: {str(e)}")
    
    def _generate_gemini_response(self, prompt: str, model: str) -> str:
        """Generate response using Google Gemini"""
        try:
            if not self.google_api_key:
                raise ValueError("GOOGLE_API_KEY is missing. Please set it in backend/.env")
            
            # Debug: Log the incoming model name
            print(f"[DEBUG] Received model name: '{model}' (type: {type(model)})")
            
            # Normalize model name (handle None, empty strings, case variations)
            if not model or model == "None" or str(model).strip() == "":
                print("[DEBUG] No model specified, using default 'gemini-2.5-flash'")
                model_name = "gemini-2.5-flash"
            else:
                model_str = str(model).strip()
                model_lower = model_str.lower()
                
                # Map old model names to new available models based on current API list
                if "flash" in model_lower:
                    model_name = "gemini-2.5-flash"
                elif "pro" in model_lower:
                    model_name = "gemini-2.5-pro"
                else:
                    model_name = "gemini-2.5-flash"
            
            # Try the model with fast fallback
            # Based on current API, 1.5 is missing, 2.5 and 2.0 are present
            try_models = [model_name]
            
            # Add reliable fallbacks from the verified list
            fallbacks = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest", "gemini-pro-latest"]
            for f in fallbacks:
                if f not in try_models:
                    try_models.append(f)
            
            last_error = None
            
            for attempt_model in try_models:
                try:
                    print(f"[DEBUG] Trying model: '{attempt_model}'")
                    # Use models/ prefix if not present
                    full_model_name = attempt_model if attempt_model.startswith("models/") else f"models/{attempt_model}"
                    gemini_model = genai.GenerativeModel(full_model_name)
                    response = gemini_model.generate_content(prompt)
                    
                    # Safety check for response
                    if not response:
                        print(f"[DEBUG] Model '{attempt_model}' returned empty response")
                        continue
                        
                    print(f"[DEBUG] Successfully used model: '{attempt_model}'")
                    return response.text
                except Exception as e:
                    error_str = str(e)
                    last_error = error_str
                    
                    # Handle model not found (404)
                    if "404" in error_str or "not found" in error_str.lower():
                        print(f"[DEBUG] Model '{attempt_model}' not found. Trying next...")
                        continue

                    # Handle rate limit (429)
                    if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                        print(f"[DEBUG] Rate limit hit for '{attempt_model}'")
                        
                        # If it's a daily quota error, don't wait, just try next model
                        if "Daily" in error_str or "quota exceeded" in error_str.lower():
                            print(f"[DEBUG] Daily quota reached for '{attempt_model}', trying next model immediately...")
                            continue
                        
                        # If it's a per-minute limit (RPM), wait briefly only if we haven't tried all models
                        import re
                        delay_match = re.search(r'retry in (\d+\.?\d*)s', error_str, re.IGNORECASE)
                        wait_time = float(delay_match.group(1)) if delay_match else 2
                        
                        if wait_time > 10: wait_time = 2 # Don't wait too long for chat
                        
                        print(f"[DEBUG] RPM limit hit. Waiting {wait_time}s before trying next...")
                        time.sleep(wait_time)
                        continue
                        
                    print(f"[DEBUG] Model '{attempt_model}' failed: {error_str[:100]}")
                    continue
            
            # If all Gemini models failed, and we have OpenAI key, try OpenAI as a last resort!
            if self.openai_api_key:
                print("[DEBUG] All Gemini models failed. Trying OpenAI as fallback...")
                try:
                    return self._generate_openai_response(prompt, "gpt-3.5-turbo")
                except Exception as oa_err:
                    print(f"[DEBUG] OpenAI fallback also failed: {oa_err}")
            
            # If still nothing, raise error
            if "quota" in str(last_error).lower() or "429" in str(last_error):
                raise Exception(f"Google API rate limit exceeded. Your daily quota might be finished. Please try creating a NEW API key in a NEW Google Cloud project.")
            raise Exception(f"All LLM models failed. Last error: {last_error}")
            
            # If all models failed, raise error with helpful message
            if "quota" in str(last_error).lower() or "429" in str(last_error):
                raise Exception(f"Google API rate limit exceeded. Your daily quota might be finished. Please try creating a NEW API key in a NEW Google Cloud project.")
            raise Exception(f"All Gemini models failed. Last error: {last_error}")
            
            # If all models failed, raise error
            raise Exception(f"All Gemini models failed. Last error: {last_error}")
        except Exception as e:
            raise Exception(f"Error generating Gemini response: {str(e)}")
    
    def _web_search(self, query: str) -> Optional[Dict]:
        """Perform web search using SerpAPI or Brave Search"""
        # Try SerpAPI first
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        if serpapi_key:
            try:
                from serpapi import GoogleSearch
                search = GoogleSearch({
                    "q": query,
                    "api_key": serpapi_key
                })
                results = search.get_dict()
                return {
                    "source": "serpapi",
                    "results": results.get("organic_results", [])[:5]
                }
            except Exception as e:
                print(f"SerpAPI error: {e}")
        
        # Fallback to Brave Search
        brave_key = os.getenv("BRAVE_API_KEY")
        if brave_key:
            try:
                from brave_search import Brave
                brave = Brave(api_key=brave_key)
                results = brave.search(q=query, count=5)
                return {
                    "source": "brave",
                    "results": results.get("web", {}).get("results", [])
                }
            except Exception as e:
                print(f"Brave Search error: {e}")
        
        return None
