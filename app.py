from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "godmoded/llama3-lexi-uncensored:latest"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lexi AI Chat</title>
    <style>
        :root {
            --bg: #120005;
            --panel: #1f0a0f;
            --panel-border: #660000;
            --text: #f4e7e7;
            --muted: #c8b5b5;
            --accent: #ff2a2a;
            --input-bg: #2b1518;
            --button-bg: #ff2a2a;
            --button-hover: #dc1f1f;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            background: radial-gradient(circle at top, #3f0505 0%, #120005 45%, #050202 100%);
            color: var(--text);
            font-family: Inter, Arial, sans-serif;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 30px 20px 40px;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 26px;
        }

        .logo {
            width: 52px;
            height: 52px;
            border-radius: 14px;
            background: linear-gradient(135deg, #ff2a2a 0%, #a70000 100%);
            display: grid;
            place-items: center;
            box-shadow: 0 0 28px rgba(255, 42, 42, 0.3);
        }

        .logo span {
            font-size: 26px;
            font-weight: 800;
            color: white;
            letter-spacing: -1px;
        }

        .brand-title {
            display: grid;
            gap: 4px;
        }

        .brand-title h1 {
            margin: 0;
            font-size: 2rem;
        }

        .brand-title p {
            margin: 0;
            color: var(--muted);
        }

        .panel {
            background: rgba(18, 0, 5, 0.85);
            border: 1px solid var(--panel-border);
            border-radius: 24px;
            box-shadow: 0 18px 60px rgba(0, 0, 0, 0.45);
            overflow: hidden;
        }

        #chat {
            min-height: 420px;
            max-height: 520px;
            padding: 24px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }

        .bubble {
            padding: 16px 18px;
            border-radius: 18px;
            line-height: 1.65;
            max-width: 82%;
            white-space: pre-wrap;
            word-break: break-word;
        }

        .bubble.user {
            align-self: flex-end;
            background: rgba(255, 42, 42, 0.15);
            border: 1px solid rgba(255, 42, 42, 0.35);
            color: #ffe6e6;
        }

        .bubble.ai {
            align-self: flex-start;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: var(--text);
        }

        .composer {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 12px;
            padding: 20px;
            border-top: 1px solid rgba(255, 42, 42, 0.18);
            background: rgba(18, 0, 5, 0.95);
        }

        .composer input {
            width: 100%;
            padding: 16px 18px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: var(--input-bg);
            color: var(--text);
            font-size: 1rem;
        }

        .composer input:focus {
            outline: 2px solid rgba(255, 42, 42, 0.55);
        }

        .composer button {
            border: none;
            border-radius: 16px;
            padding: 16px 24px;
            background: var(--button-bg);
            color: white;
            font-weight: 700;
            cursor: pointer;
            transition: background 0.2s ease;
        }

        .composer button:hover {
            background: var(--button-hover);
        }

        @media (max-width: 640px) {
            .container {
                padding: 20px 12px 30px;
            }

            .brand-title h1 {
                font-size: 1.5rem;
            }

            .composer {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="brand">
            <div class="logo"><span>G</span></div>
            <div class="brand-title">
                <h1>Betten</h1>
                <p>The AI you use to build your creative ideas.</p>
            </div>
        </div>

        <div class="panel">
            <div id="chat"></div>
            <form class="composer" id="chat-form" onsubmit="handleSubmit(event)">
                <input type="text" id="message" placeholder="Type your message and press Enter..." autocomplete="off" />
                <button type="submit">Send</button>
            </form>
        </div>
    </div>

    <script>
        const form = document.getElementById('chat-form');
        const input = document.getElementById('message');

        form.addEventListener('submit', handleSubmit);

        // Initialize with greeting message
        window.addEventListener('load', () => {
            appendMessage("Hello! I'm Betten, your AI companion for building creative ideas. How can I help you today?", 'ai');
        });

        async function handleSubmit(event) {
            event.preventDefault();
            const message = input.value.trim();
            if (!message) return;
            input.value = '';
            appendMessage(message, 'user');

            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            const data = await response.json();
            appendMessage(data.response, 'ai');
        }

        function appendMessage(text, type) {
            const chat = document.getElementById('chat');
            const bubble = document.createElement('div');
            bubble.className = `bubble ${type}`;
            bubble.textContent = text;
            chat.appendChild(bubble);
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    payload = {
        "model": MODEL,
        "prompt": user_message,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response_data = response.json()
        ai_response = response_data.get('response', 'Error: No response')
    except Exception as e:
        ai_response = f'Error: {str(e)}'
    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)