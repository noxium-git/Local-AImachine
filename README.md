# Court - Local Uncensored AI

Privacy-focused AI running locally on your machine. No data collection, no external servers, and no user tracking. Designed for secure, anonymous interactions while keeping full control of your data.

Created by **Nox**.

## Features

- Local AI processing using Ollama
- Local account system with register/login (SQLite + hashed passwords)
- Beautiful black-red dark theme UI with Tailwind CSS
- ChatGPT-like interface with sidebar chat history
- Profile card with model and local health status
- Streaming responses with stop/cancel control
- Advanced generation controls (preset, temperature, top_p, top_k, max tokens)
- Local RAG knowledge base (upload files, retrieve context, cite sources)
- RAG document manager (rename/delete indexed files)
- Privacy mode toggle (ephemeral vs persistent chats)
- One-click local data wipe per account
- Animated loading indicators with custom logo
- Formatted AI responses with code highlighting
- FAQs page
- Temporary chat history (cleared on logout/server restart)

## Setup

1. Install Python dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Ensure Ollama is running with the required model:

   ```
   ollama pull godmoded/llama3-lexi-uncensored:latest
   ```

3. Run the application:

   ```
   python launcher.py
   ```

4. Open your browser to `http://localhost:5000`

5. Login with:
   - Username: admin
   - Password: admin123
6. Or create a local account from the login page.

## Evaluate Before Training

Run the local benchmark harness before you fine-tune:

1. Edit prompt cases in `eval_prompts.json`.
2. Run:
   ```
   python eval_runner.py
   ```
3. Review `eval_report.json` for latency and response quality preview.

## Refusal Reduction Workflow

Use this workflow to reduce false refusals while preserving refusals for clearly harmful requests.

1. Build dataset:
   ```
   python training_data/build_refusal_reduction_dataset.py
   ```
2. Evaluate baseline model:
   ```
   python eval_runner.py --model godmoded/llama3-lexi-uncensored:latest --report training_data/eval_report_baseline.json
   ```
3. Create Court policy model:
   ```
   python training_data/create_court_refusal_model.py --base godmoded/llama3-lexi-uncensored:latest --target court-refusal-v1
   ```
4. Evaluate policy model:
   ```
   python eval_runner.py --model court-refusal-v1 --report training_data/eval_report_target.json
   ```
5. Run full pipeline in one command:
   ```
   python training_data/run_refusal_pipeline.py
   ```
6. Launch app with target model:
   ```
   $env:COURT_MODEL='court-refusal-v1'; python app.py
   ```

## Local RAG Quick Start

1. Open Settings in chat.
2. In `Local Knowledge (RAG)`, enable retrieval.
3. Upload a local file (`.txt`, `.md`, `.py`, `.json`, `.csv`, `.html`, `.js`, `.css`, `.pdf`).
4. Ask a question related to the uploaded content.
5. Court will include a `Sources` section when context is used.
6. Use `View sources` on AI messages to inspect matched snippets.

## Privacy Controls

In Settings:

1. Choose `Privacy mode`:
   - `Ephemeral`: chats stay in session only.
   - `Persistent`: chats are saved locally per user.
2. Use `Wipe local data` to clear chats, indexed docs, and reset settings for the current account.

## Packaging

To create a local Windows package and installer:

1. Install dependencies:
   ```
   pip install pyinstaller
   ```
2. Run the build script:
   ```
   .\package.ps1
   ```
3. After building, open `BettenAIInstaller.iss` in Inno Setup and compile it to generate a Windows installer.
4. Make sure Ollama is installed locally and the model is downloaded before distributing the app.
5. For production, set a secure `COURT_SECRET_KEY` environment variable instead of using the default development placeholder.

## Project Structure

- `app.py`: Main Flask application
- `templates/`: HTML templates (login, chat, faqs)
- `static/`: CSS, JS, and image assets
- `requirements.txt`: Python dependencies

## Usage

- Start new chats from the sidebar
- View chat history in the left panel
- Access FAQs for more information
- AI responses are automatically formatted with code blocks and syntax highlighting

Enjoy your creative AI companion!
