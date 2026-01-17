import os
import time
from typing import List
import numpy as np
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        # Use Google API by default
        if self.google_api_key:
            self.default_provider = "google"
            print("EmbeddingService initialized with GOOGLE API")
        elif self.openai_api_key:
            self.default_provider = "openai"
            print("EmbeddingService initialized with OPENAI API")
        else:
            self.default_provider = "google"
            print("Warning: No API keys found!")
        
        # Track last API call time to avoid rate limits
        self._last_api_call = 0
    
    def generate_embeddings(self, texts: List[str], provider: str = None, fast_mode: bool = False) -> List[np.ndarray]:
        """Generate embeddings for a list of texts"""
        # Use default provider if not specified
        if provider is None:
            provider = self.default_provider
        
        print(f"Generating embeddings for {len(texts)} texts using {provider} (fast_mode: {fast_mode})...")
        
        if provider == "openai":
            return self._generate_openai_embeddings(texts)
        elif provider == "google":
            return self._generate_google_embeddings(texts, max_retries=1 if fast_mode else 5)
        else:
            return self._generate_google_embeddings(texts, max_retries=1 if fast_mode else 5)
    
    def _generate_openai_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings using OpenAI"""
        try:
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY is missing. Please set it in backend/.env")
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )
            embeddings = [np.array(item.embedding) for item in response.data]
            return embeddings
        except Exception as e:
            raise Exception(f"Error generating OpenAI embeddings: {str(e)}")
    
    def _generate_google_embeddings(self, texts: List[str], max_retries: int = 5) -> List[np.ndarray]:
        """Generate embeddings using Google Gemini with rate limit handling"""
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY is missing. Please set it in backend/.env")
        
        import google.generativeai as genai
        genai.configure(api_key=self.google_api_key)
        
        embeddings = []
        rate_limited = False
        
        for i, text in enumerate(texts):
            # Ultra-aggressive text cleaning: Remove ALL problematic characters
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='ignore')
            
            # Method 1: Remove all null bytes using multiple methods
            import re
            text = re.sub(r'\x00+', '', text)  # Remove null bytes with regex
            text = text.replace('\x00', '').replace('\0', '').replace('\u0000', '')
            text = text.replace(chr(0), '')  # Remove null character
            
            # Method 2: Filter out control characters (keep only printable + newline/tab)
            text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
            
            # Method 3: UTF-8 encoding/decoding to remove invalid sequences
            text = text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
            
            # Method 4: Normalize whitespace
            text = ' '.join(text.split())
            text = text.strip()
            
            # Method 5: Final validation - check for ANY null bytes
            if '\x00' in text or '\0' in text or chr(0) in text:
                print(f"ERROR: Chunk {i+1} STILL contains null bytes after cleaning!")
                # Last resort: remove ALL non-printable characters
                text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
                text = text.replace('\x00', '').replace('\0', '')
            
            # Final check: ensure no null bytes remain
            if '\x00' in text or '\0' in text:
                print(f"ERROR: Chunk {i+1} cannot be cleaned, skipping...")
                continue
            
            if not text or len(text) < 10:
                print(f"Warning: Chunk {i+1} is too short or empty, skipping...")
                continue
            
            # Log cleaned text length
            print(f"Chunk {i+1} cleaned: {len(text)} characters, no null bytes: {chr(0) not in text}")
            
            # Wait between API calls to avoid rate limit (15 req/min = 5 sec between calls)
            time_since_last = time.time() - self._last_api_call
            if time_since_last < 5:
                wait_time = 5 - time_since_last
                print(f"Waiting {wait_time:.1f}s to avoid rate limit...")
                time.sleep(wait_time)
            
            for attempt in range(max_retries):
                try:
                    # Final validation right before API call
                    if '\x00' in text or '\0' in text or chr(0) in text:
                        raise ValueError("Text contains null bytes and cannot be sent to API")
                    
                    # Safe print (avoid Unicode issues on Windows)
                    try:
                        print(f"Embedding chunk {i+1}/{len(texts)} (attempt {attempt+1})...")
                        safe_preview = text[:100].encode('ascii', errors='replace').decode('ascii')
                        print(f"Text preview: {safe_preview}...")
                        print(f"Text length: {len(text)}, Has null bytes: {chr(0) in text}")
                    except:
                        pass  # Skip print if encoding fails
                    
                    result = genai.embed_content(
                        model="models/embedding-001",
                        content=text,
                        task_type="retrieval_document"
                    )
                    embeddings.append(np.array(result['embedding']))
                    self._last_api_call = time.time()
                    print(f"[OK] Chunk {i+1} embedded successfully!")
                    break
                    
                except Exception as e:
                    error_str = str(e)
                    # Safe print (avoid Unicode issues on Windows)
                    try:
                        safe_error = error_str[:200].encode('ascii', errors='replace').decode('ascii')
                        print(f"[ERROR] Error on attempt {attempt+1}: {safe_error}...")
                    except:
                        print(f"[ERROR] Error on attempt {attempt+1}")
                    
                    if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "retryDelay" in error_str or "quota" in error_str.lower():
                        # Extract retry delay from error if available
                        import re
                        delay_match = re.search(r'retry in (\d+\.?\d*)s', error_str, re.IGNORECASE)
                        if delay_match:
                            wait_time = float(delay_match.group(1)) + 5  # Add buffer
                        else:
                            wait_time = (attempt + 1) * 20  # 20, 40, 60, 80, 100 seconds
                        
                        print(f"Rate limit/quota hit! Waiting {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        
                        if attempt == max_retries - 1:
                            print("Rate limit persists after retries. Skipping embeddings for this upload.")
                            rate_limited = True
                            break
                    elif "NUL" in error_str or "0x00" in error_str:
                        # NUL character error - should not happen after cleaning, but handle it
                        print("NUL character detected, cleaning text...")
                        text = text.replace('\x00', '').replace('\0', '')
                        if attempt == max_retries - 1:
                            raise Exception("PDF contains invalid characters that cannot be processed.")
                    else:
                        raise Exception(f"Error generating Google embeddings: {error_str[:500]}")
            
            if rate_limited:
                break
        
        if len(embeddings) == 0:
            print("No embeddings generated. Proceeding without embeddings.")
            return []
        
        print(f"[OK] Successfully generated {len(embeddings)} embeddings!")
        return embeddings
