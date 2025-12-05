"""
Main entry point for the Mauritania Chatbot application
"""
import os
from dotenv import load_dotenv
from ui.interface import create_ui
from config import APP_PORT, APP_HOST, GROQ_API_KEY


def main():
    """Main application entry point"""
    print("\n" + "=" * 50)
    print("🇲🇷 MAURITANIA CHATBOT")
    print("=" * 50 + "\n")
    
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment or config
    api_key = os.getenv("GROQ_API_KEY", GROQ_API_KEY)
    
    if not api_key or api_key == "your_api_key_here":
        print("⚠️ WARNING: No valid Groq API key found!")
        print("Please set GROQ_API_KEY in .env file or config.py")
    
    try:
        # Create and launch interface
        demo = create_ui(api_key)
        demo.launch(
            server_name=APP_HOST,
            server_port=APP_PORT,
            share=False,  # Set to True for temporary public sharing
            debug=False
        )
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()