"""
Main chatbot class that orchestrates RAG and Groq integration
"""
import time
from core.rag_system import RAGSystem
from core.groq_client import GroqClient


class MauritaniaChatbot:
    def __init__(self, groq_api_key: str):
        print("🚀 Initializing chatbot...")
        self.rag = RAGSystem()
        self.groq = GroqClient(groq_api_key)
        print("✅ Chatbot ready!")
    
    def _build_local_reply(self, svc, lang):
        """Build a safe fallback reply in the requested language"""
        if lang == "ar":
            resp = f"**{svc['name_ar']}**\n\n{svc.get('description','')}\n\n"
            if 'documents_required' in svc:
                resp += "📋 **الوثائق المطلوبة:**\n"
                for doc in svc['documents_required']:
                    resp += f"• {doc}\n"
            if 'cost' in svc:
                resp += f"\n💰 **التكلفة:** {svc['cost']}"
            if 'duration' in svc:
                resp += f"\n⏱️ **المدة:** {svc['duration']}"
            return resp
        else:
            resp = f"**{svc['name_fr']}**\n\n{svc.get('description','')}\n\n"
            if 'documents_required' in svc:
                resp += "📋 **Documents requis:**\n"
                for doc in svc['documents_required']:
                    resp += f"• {doc}\n"
            if 'cost' in svc:
                resp += f"\n💰 **Coût:** {svc['cost']}"
            if 'duration' in svc:
                resp += f"\n⏱️ **Durée:** {svc['duration']}"
            return resp
    
    def _build_context(self, svc):
        """Build context text for the LLM"""
        context = f"Service: {svc['name_fr']} / {svc['name_ar']}\n\nDescription: {svc.get('description','')}\n\n"
        
        if 'documents_required' in svc:
            context += "Documents requis:\n"
            for doc in svc['documents_required']:
                context += f"- {doc}\n"
            context += "\n"
        
        if 'steps' in svc:
            context += "Étapes:\n"
            for i, step in enumerate(svc['steps'], 1):
                context += f"{i}. {step}\n"
            context += "\n"
        
        if 'payment_methods' in svc:
            context += "Méthodes de paiement:\n"
            for method in svc['payment_methods']:
                context += f"{method}\n"
            context += "\n"
        
        if 'cost' in svc:
            context += f"Coût: {svc['cost']}\n"
        if 'duration' in svc:
            context += f"Durée: {svc['duration']}\n"
        if 'office' in svc:
            context += f"Bureau: {svc['office']}\n"
        
        return context
    
    def _get_system_prompt(self, lang):
        """Get system prompt based on language"""
        if lang == "ar":
            return """أنت مساعد ذكي للخدمات العامة الموريتانية.

مهمتك:
- أجب على أسئلة المواطنين بوضوح ودقة
- استخدم فقط المعلومات المقدمة
- أجب باللغة العربية بشكل طبيعي
- كن مختصراً ومباشراً

أسلوبك: ودي، واضح، منظم
"""
        else:
            return """Vous êtes un assistant intelligent pour les services publics mauritaniens.

Votre mission:
- Répondez aux questions avec clarté
- Utilisez uniquement les informations fournies
- Répondez en français naturellement
- Soyez concis et direct

Votre style: amical, clair, organisé
"""
    
    def answer(self, query: str, lang: str = "fr"):
        """
        Main method to answer user queries
        
        Args:
            query: User question
            lang: Response language ('fr' or 'ar')
            
        Returns:
            Formatted answer
        """
        # Search for relevant services
        results = self.rag.search(query)
        
        if not results:
            if lang == "ar":
                return "⚠️ لم أجد معلومات عن هذا السؤال.\n\nيرجى إعادة صياغة سؤالك."
            else:
                return "⚠️ Je n'ai pas trouvé d'informations sur cette question.\n\nVeuillez reformuler."
        
        svc = results[0]['svc']
        context = self._build_context(svc)
        system_prompt = self._get_system_prompt(lang)
        
        # Try to use Groq if available
        if self.groq.available:
            full_context = f"{context}\n\nQuestion: {query}"
            response = self.groq.generate(system_prompt, full_context, lang=lang)
            
            if response:
                source_label = svc['name_ar'] if lang == "ar" else svc['name_fr']
                return f"{response}\n\n📚 Source: {source_label}"
        
        # Fallback to local reply
        local = self._build_local_reply(svc, lang)
        source_label = svc['name_ar'] if lang == "ar" else svc['name_fr']
        return f"{local}\n\n📚 Source: {source_label}"