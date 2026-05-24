import os
import chainlit as cl
import logging

# Add src to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.analyzer import FinancialAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

analyzer = None

@cl.on_chat_start
async def on_chat_start():
    global analyzer
    
    try:
        analyzer = FinancialAnalyzer()
        
        # Welcome message
        welcome_msg = cl.Message(
            content="""
            # 🏦 FinOps AI Analyst (Simplified Edition)
            
            Welcome! I am a 100% open-source, locally-running Financial Analysis AI.
            
            **How to use:**
            1. Click the attachment icon (📎) below to upload a quarterly financial report (PDF).
            2. I will read the report, evaluate the company's health, and give you a **BUY**, **HOLD**, or **SELL** rating.
            
            Upload a PDF to get started!
            """
        )
        await welcome_msg.send()
        logger.info("Chat session initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize chat session: {e}")
        error_msg = cl.Message(
            content=f"⚠️ Initialization Error: {str(e)}\n\nPlease ensure Ollama is running."
        )
        await error_msg.send()


@cl.on_message
async def on_message(message: cl.Message):
    global analyzer
    
    # Check if a file was uploaded
    if not message.elements:
        await cl.Message(content="Please upload a PDF financial report using the attachment icon (📎).").send()
        return

    # Process the first uploaded file
    file = message.elements[0]
    
    if not file.name.lower().endswith('.pdf'):
        await cl.Message(content="Please upload a valid PDF file.").send()
        return

    # Show thinking indicator
    thinking_msg = cl.Message(content="🤔 Reading the PDF and analyzing financial health. This might take a minute depending on your hardware...")
    await thinking_msg.send()
    
    try:
        # Run the evaluation
        # file.path contains the local path to the uploaded file
        result = analyzer.evaluate_report(file.path)
        
        # Delete thinking message
        await thinking_msg.remove()
        
        # Send final answer
        response_msg = cl.Message(content=result)
        await response_msg.send()
        
    except Exception as e:
        logger.error(f"Failed to process document: {e}")
        await thinking_msg.remove()
        error_msg = cl.Message(
            content=f"❌ Error evaluating the report: {str(e)}"
        )
        await error_msg.send()


if __name__ == "__main__":
    import chainlit as cl
    cl.run()
