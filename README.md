# Betten AI - Local Uncensored AI

Privacy-focused AI running locally on your machine. No data collection, no external servers, and no user tracking. Designed for secure, anonymous interactions while keeping full control of your data.

Created by **Nox**.

## Features

- Local AI processing using Ollama
- Beautiful black-red dark theme UI with Tailwind CSS
- ChatGPT-like interface with sidebar chat history
- Secure login system
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
   python app.py
   ```

4. Open your browser to `http://localhost:5000`

5. Login with:
   - Username: admin
   - Password: admin123

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
