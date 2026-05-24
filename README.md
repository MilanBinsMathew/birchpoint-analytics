# FinOps AI Analyst (Lightweight Native Edition)

An open-source Financial Analysis AI system configured to run quickly and efficiently as a lightweight local application. It leverages your machine's native hardware (like the Apple Silicon M3 GPU) via Ollama, completely bypassing heavy virtualization layers like Docker.

## Features

- **Fast Local Inference**: Uses the native Ollama application to run `llama3:8b` directly on your Mac's GPU (Metal framework).
- **Simple PDF Analysis**: Reads and evaluates financial PDFs offline.
- **Enterprise UI**: Premium Chainlit interface.
- **100% Privacy**: All documents and models run locally, ensuring financial data never leaves your machine.

## Tech Stack

- **LLM**: Llama-3 (8B) via Native Ollama
- **PDF Parsing**: `pdfplumber`
- **UI**: Chainlit

## Setup Instructions

### Prerequisites

- Mac with Apple Silicon (M1/M2/M3) recommended for performance.
- Python 3.9+
- **[Ollama](https://ollama.com/)** (Native Application, not via Docker)

### Quick Start

1. **Install Ollama**
   Download and install Ollama from [ollama.com](https://ollama.com/).
   *Important*: Open the Ollama app from your Applications folder so it runs in your menu bar.

2. **Clone the repository (if you haven't already):**
   ```bash
   git clone <repository-url>
   cd birchpoint-analytics
   ```

3. **Run the startup script:**
   ```bash
   ./start.sh
   ```

   This script will:
   - Check if Ollama is running
   - Pull the required `llama3:8b` model
   - Create a Python virtual environment (`.venv`)
   - Install required Python dependencies
   - Create necessary data directories

4. **Start the application:**
   ```bash
   source .venv/bin/activate
   chainlit run app.py
   ```

   The UI will be available at `http://localhost:8000`

## Usage

1. Open `http://localhost:8000` in your browser.
2. Click the attachment icon (📎) in the chat bar to upload a quarterly financial report (PDF).
3. The AI will read the report, evaluate the company's health, and give you a **BUY**, **HOLD**, or **SELL** rating.

## License

See LICENSE file for details.
