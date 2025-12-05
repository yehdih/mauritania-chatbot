"""
Gradio user interface for the chatbot
"""
import gradio as gr
import time
from core.chatbot import MauritaniaChatbot
from services.database import SERVICES_DB
from config import APP_TITLE, APP_DESCRIPTION


def create_ui(api_key: str):
    """Create and configure the Gradio interface"""
    bot = MauritaniaChatbot(api_key)
    
    def normalize_history(history):
        """
        Normalize older tuple-style history into list of dict messages
        """
        if not history:
            return []
        
        normalized = []
        for item in history:
            if isinstance(item, dict):
                if 'role' in item and 'content' in item:
                    normalized.append(item)
                else:
                    continue
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                user_text, assistant_text = item
                normalized.append({'role': 'user', 'content': str(user_text)})
                normalized.append({'role': 'assistant', 'content': str(assistant_text)})
            else:
                continue
        return normalized
    
    def chat_fn(msg, history, lang):
        """Handle chat interactions"""
        if not msg or not msg.strip():
            return history or [], ""
        
        start = time.time()
        resp = bot.answer(msg, lang)
        elapsed = time.time() - start
        resp_with_time = f"{resp}\n\n⚡ {elapsed:.2f}s"
        
        history_msgs = normalize_history(history)
        history_msgs.append({'role': 'user', 'content': str(msg)})
        history_msgs.append({'role': 'assistant', 'content': resp_with_time})
        
        return history_msgs, ""
    
    def get_services(lang):
        """Get list of available services for display"""
        lines = ["### 📋 Services:\n"]
        for svc in SERVICES_DB.values():
            name = svc['name_ar'] if lang == "ar" else svc['name_fr']
            lines.append(f"• {name}")
        return "\n".join(lines)
    
    def create_quick_questions():
        """Create quick question buttons"""
        questions = {
            "fr": [
                ("💳 Carte d'identité?", "Comment obtenir une carte d'identité?"),
                ("✈️ Passeport?", "Quels documents pour le passeport?"),
                ("⚡ SOMELEC?", "Comment payer SOMELEC?"),
                ("🚗 Permis?", "Comment obtenir un permis?"),
                ("🏥 Hôpital?", "Rendez-vous hôpital?")
            ],
            "ar": [
                ("بطاقة تعريف؟", "كيف أحصل على بطاقة تعريف؟"),
                ("جواز سفر؟", "ما هي وثائق جواز السفر؟"),
                ("فاتورة كهرباء؟", "كيف أدفع فاتورة الكهرباء؟")
            ]
        }
        return questions
    
    # Create interface
    with gr.Blocks(title=APP_TITLE, theme=gr.themes.Soft()) as demo:
        # Header
        gr.Markdown(f"# {APP_TITLE}")
        gr.Markdown(f"## {APP_DESCRIPTION}")
        
        # Status warning
        if not bot.groq.available:
            gr.Markdown("""
            ### ⚠️ API non connectée
            
            Vérifiez votre clé API Groq dans le code.
            """)
        
        with gr.Row():
            # Main chat area
            with gr.Column(scale=3):
                lang = gr.Radio(
                    choices=[("🇫🇷 Français", "fr"), ("🇲🇷 العربية", "ar")],
                    value="fr",
                    label="Langue / اللغة"
                )
                
                chatbot_ui = gr.Chatbot(
                    height=500,
                    label="💬 Chat / محادثة",
                    bubble_full_width=False
                )
                
                with gr.Row():
                    msg_box = gr.Textbox(
                        placeholder="Votre question... / سؤالك...",
                        label="Message / رسالة",
                        scale=4,
                        autofocus=True
                    )
                    send = gr.Button("📤", scale=1, variant="primary")
                
                clear = gr.Button("🗑️ Effacer / مسح", size="sm")
                
                status_text = "✅ Groq connecté!" if bot.groq.available else "⚠️ Mode hors ligne"
                status = gr.Markdown(f"**Status:** {status_text}")
            
            # Sidebar with services and quick questions
            with gr.Column(scale=1):
                services = gr.Markdown()
                
                gr.Markdown("### 🚀 Questions rapides / أسئلة سريعة")
                
                # Create quick question buttons
                questions = create_quick_questions()
                
                # French questions
                for btn_text, question in questions["fr"]:
                    btn = gr.Button(btn_text, size="sm", min_width=150)
                    btn.click(lambda q=question: q, outputs=msg_box)
                
                gr.Markdown("---")
                
                # Arabic questions
                for btn_text, question in questions["ar"]:
                    btn = gr.Button(btn_text, size="sm", min_width=150)
                    btn.click(lambda q=question: q, outputs=msg_box)
                
                gr.Markdown("---")
                gr.Markdown(f"""
                ### ℹ️ Info / معلومات
                
                **Modèle / النموذج:** {bot.groq.__class__.__name__}  
                **Services / الخدمات:** {len(SERVICES_DB)}
                **Base de données / قاعدة البيانات:** {len(bot.rag.kb)} documents
                """)
        
        # Event handlers
        lang.change(get_services, inputs=[lang], outputs=[services])
        demo.load(lambda: get_services("fr"), outputs=[services])
        
        send.click(chat_fn, [msg_box, chatbot_ui, lang], [chatbot_ui, msg_box])
        msg_box.submit(chat_fn, [msg_box, chatbot_ui, lang], [chatbot_ui, msg_box])
        clear.click(lambda: [], outputs=[chatbot_ui])
    
    return demo