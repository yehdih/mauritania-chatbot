"""
Groq API client with robust response parsing and language checking
"""
import re
from groq import Groq

from config import GROQ_MODEL


class GroqClient:
    def __init__(self, api_key: str):
        if not api_key:
            print("⚠️ WARNING: No Groq API key!")
            self.client = None
            self.available = False
        else:
            try:
                self.client = Groq(api_key=api_key)
                # Test connection
                try:
                    self.client.chat.completions.create(
                        messages=[{"role": "user", "content": "test"}],
                        model=GROQ_MODEL,
                        max_tokens=5
                    )
                    print(f"✅ Groq API connected! Using {GROQ_MODEL}")
                    self.available = True
                except Exception as e:
                    print(f"⚠️ Groq test request failed: {e}")
                    self.available = True  # Keep True for individual call handling
            except Exception as e:
                print(f"❌ Groq API init error: {e}")
                self.client = None
                self.available = False
    
    def _extract_content_from_response(self, response):
        """
        Try several ways to extract textual content from various SDK response shapes
        
        Args:
            response: Raw response from Groq API
            
        Returns:
            Extracted text content or None
        """
        try:
            # 1) attribute-style: response.choices[0].message.content
            if hasattr(response, "choices"):
                choices = response.choices
                if len(choices) > 0:
                    c0 = choices[0]
                    # try c0.message.content
                    if hasattr(c0, "message"):
                        msg = c0.message
                        if hasattr(msg, "content"):
                            return msg.content
                        if isinstance(msg, dict) and "content" in msg:
                            return msg["content"]
                    # try c0.text or c0["text"]
                    if hasattr(c0, "text"):
                        return c0.text
                    if isinstance(c0, dict):
                        for k in ("message", "text", "content"):
                            if k in c0:
                                val = c0[k]
                                if isinstance(val, dict) and "content" in val:
                                    return val["content"]
                                if isinstance(val, str):
                                    return val
            # 2) dict-like response
            if isinstance(response, dict):
                choices = response.get("choices", [])
                if choices:
                    c0 = choices[0]
                    if isinstance(c0, dict):
                        if "message" in c0 and isinstance(c0["message"], dict) and "content" in c0["message"]:
                            return c0["message"]["content"]
                        for k in ("text", "content"):
                            if k in c0 and isinstance(c0[k], str):
                                return c0[k]
            # 3) fallback to string representation if short
            s = str(response)
            if len(s) < 1000:
                return s
        except Exception:
            pass
        return None
    
    def _is_response_in_lang(self, text: str, lang: str) -> bool:
        """Check if response is in the expected language"""
        if not text or not isinstance(text, str):
            return False
        if lang == "ar":
            return bool(re.search(r'[\u0600-\u06FF]', text))
        else:
            return bool(re.search(r'[A-Za-z]', text))
    
    def generate(self, system_prompt: str, user_message: str, lang: str = "fr"):
        """
        Generate response using Groq API
        
        Args:
            system_prompt: System instruction
            user_message: User query
            lang: Target language ('fr' or 'ar')
            
        Returns:
            Generated text or None
        """
        if not self.available or not self.client:
            return None
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                model=GROQ_MODEL,
                temperature=0.7,
                max_tokens=500,
                top_p=0.9
            )
            
            content = self._extract_content_from_response(response)
            
            # Validate response
            if not content:
                return None
            if not self._is_response_in_lang(content, lang):
                return None
            
            return content.strip()
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return None