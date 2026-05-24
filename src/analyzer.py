import os
import pdfplumber
import logging
from typing import Optional
from .utils.ollama_client import OllamaManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialAnalyzer:
    def __init__(self):
        self.ollama_manager = OllamaManager()
        # Default model is configured in OllamaManager, usually llama3:8b

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise
        return text

    def evaluate_report(self, pdf_path: str) -> str:
        # 1. Extract text
        logger.info(f"Extracting text from {pdf_path}")
        document_text = self.extract_text_from_pdf(pdf_path)
        
        # We might need to truncate if the text is massive, 
        # but for an 8B model context window (typically 8k), let's keep it reasonable.
        # We'll take the first 25000 characters to be safe.
        max_chars = 25000
        if len(document_text) > max_chars:
            document_text = document_text[:max_chars] + "\n...[truncated]..."

        # 2. Build the prompt
        prompt = f"""
You are a highly experienced financial analyst. You have been given the quarterly financial statements of a company.
Based ONLY on the provided text, evaluate the company according to the following criteria:

1. Company Health: Assess the revenue, profits, margins, and debt if mentioned.
2. Segment Health: Analyze the performance of different business segments if mentioned.
3. Market Comparison: Briefly compare how this performance stacks up against general market conditions or competitors (use your general knowledge).
4. Final Rating: Provide a definitive "BUY", "HOLD", or "SELL" rating based on the analysis.

Document Text:
{document_text}

Provide the evaluation in a clear, professional format. Ensure the final rating is prominent.
"""

        # 3. Call Ollama
        logger.info("Sending prompt to Ollama for evaluation...")
        try:
            # We can use the existing generate method
            response = self.ollama_manager.generate(prompt, temperature=0.2, max_tokens=2000)
            return response
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return "Error: Could not generate evaluation. Ensure Ollama is running and the model is downloaded."
