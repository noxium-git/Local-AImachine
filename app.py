from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, make_response
import requests
import os
import json
import markdown

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "godmoded/llama3-lexi-uncensored:latest"
DATA_FILE = os.path.join(app.root_path, 'storage.json')
DEFAULT_SYSTEM_PROMPT = (
    "You are Betten, a powerful local AI assistant. Respond clearly, helpfully, and keep answers concise. "
    "Use the context of the user's request and format code or tables when relevant."
)

def load_storage():
    if not os.path.exists(DATA_FILE):
        return {
            'chats': [],
            'current_chat_index': -1,
            'system_prompt': DEFAULT_SYSTEM_PROMPT,
        }
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (ValueError, IOError):
        return {
            'chats': [],
            'current_chat_index': -1,
            'system_prompt': DEFAULT_SYSTEM_PROMPT,
        }


def save_storage(system_prompt):
    storage = {
        'system_prompt': system_prompt,
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(storage, f, indent=2, ensure_ascii=False)


def sync_session_to_disk():
    save_storage(
        session.get('system_prompt', DEFAULT_SYSTEM_PROMPT),
    )

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session.clear()  # Clear all session data for untraceability
            session['logged_in'] = True
            storage = load_storage()
            session['system_prompt'] = storage.get('system_prompt', DEFAULT_SYSTEM_PROMPT)
            return redirect(url_for('chat'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/chat')
def chat():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    chats = session.get('chats', [])
    current_chat_index = session.get('current_chat_index', -1)
    if not chats:
        chats.append({'title': 'New Chat', 'messages': [{'type': 'ai', 'message': 'Welcome to Betten AI! I\'m your local AI assistant. How can I help you today?'}]})
        current_chat_index = 0
        session['chats'] = chats
        session['current_chat_index'] = current_chat_index
    system_prompt = session.get('system_prompt', DEFAULT_SYSTEM_PROMPT)
    response = make_response(render_template(
        'chat.html',
        chats=chats,
        current_chat_index=current_chat_index,
        system_prompt=system_prompt,
    ))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/faqs')
def faqs():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('faqs.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='images/bettenLocal.jpg'))

@app.route('/api/chat', methods=['POST'])
def api_chat():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    user_message = data.get('message', '')
    chats = session.get('chats', [])
    current_index = session.get('current_chat_index', -1)
    
    if current_index == -1 or current_index >= len(chats):
        # Create new chat with default user name placeholder
        chats.append({'title': 'New Chat', 'messages': []})
        current_index = len(chats) - 1
        session['current_chat_index'] = current_index
    
    chats[current_index]['messages'].append({'type': 'user', 'message': user_message})
    
    system_prompt = session.get('system_prompt', DEFAULT_SYSTEM_PROMPT)
    prompt_payload = f"System: {system_prompt}\n\nUser: {user_message}\nAssistant:"
    payload = {
        "model": MODEL,
        "prompt": prompt_payload,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        response_data = response.json()
        ai_response = response_data.get('response', 'Error: No response')
        formatted_response = markdown.markdown(
            ai_response,
            extensions=['fenced_code', 'tables', 'sane_lists', 'nl2br'],
            output_format='html5'
        )
    except requests.exceptions.Timeout:
        formatted_response = 'Error: AI response timed out. Please try again or allow more time for longer code answers.'
    except requests.exceptions.RequestException as e:
        formatted_response = f'Error: AI request failed ({e})'
    except ValueError:
        formatted_response = 'Error: Invalid response from AI service.'
    
    chats[current_index]['messages'].append({'type': 'ai', 'message': formatted_response})
    
    session['chats'] = chats
    return jsonify({'response': formatted_response, 'title': chats[current_index]['title'], 'chats': chats, 'current_index': current_index})

@app.route('/api/new_chat', methods=['POST'])
def new_chat():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    chats = session.get('chats', [])
    chats.append({'title': 'New Chat', 'messages': []})
    session['chats'] = chats
    current_index = len(chats) - 1
    session['current_chat_index'] = current_index
    return jsonify({'success': True, 'chats': chats, 'current_index': current_index})

@app.route('/api/load_chat/<int:index>', methods=['POST'])
def load_chat(index):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    chats = session.get('chats', [])
    if index < 0 or index >= len(chats):
        return jsonify({'error': 'Invalid chat index'}), 400
    session['current_chat_index'] = index
    return jsonify({'success': True})

@app.route('/api/save_settings', methods=['POST'])
def save_settings():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json() or {}
    system_prompt = (data.get('system_prompt') or DEFAULT_SYSTEM_PROMPT).strip() or DEFAULT_SYSTEM_PROMPT
    session['system_prompt'] = system_prompt
    sync_session_to_disk()
    return jsonify({'success': True, 'system_prompt': system_prompt})

@app.route('/api/import_chats', methods=['POST'])
def import_chats():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json() or {}
    imported_data = data.get('imported_chats')
    if isinstance(imported_data, dict):
        if 'chats' in imported_data and isinstance(imported_data['chats'], list):
            imported_chats = imported_data['chats']
        elif 'chat' in imported_data and isinstance(imported_data['chat'], dict):
            imported_chats = [imported_data['chat']]
        else:
            imported_chats = []
        system_prompt = imported_data.get('system_prompt', session.get('system_prompt', DEFAULT_SYSTEM_PROMPT))
    elif isinstance(imported_data, list):
        imported_chats = imported_data
        system_prompt = session.get('system_prompt', DEFAULT_SYSTEM_PROMPT)
    else:
        return jsonify({'error': 'Invalid import format'}), 400

    valid_chats = [
        chat for chat in imported_chats
        if isinstance(chat, dict) and 'title' in chat and 'messages' in chat
    ]
    session['chats'] = valid_chats
    session['current_chat_index'] = len(valid_chats) - 1 if valid_chats else -1
    session['system_prompt'] = system_prompt
    return jsonify({
        'success': True,
        'chats': valid_chats,
        'current_index': session['current_chat_index'],
    })

@app.route('/api/rename_chat/<int:index>', methods=['POST'])
def rename_chat(index):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json() or {}
    new_title = (data.get('title') or '').strip() or 'New Chat'
    chats = session.get('chats', [])
    if index < 0 or index >= len(chats):
        return jsonify({'error': 'Invalid chat index'}), 400
    chats[index]['title'] = new_title
    session['chats'] = chats
    return jsonify({'success': True, 'chats': chats})

@app.route('/api/delete_chat/<int:index>', methods=['POST'])
def delete_chat(index):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    chats = session.get('chats', [])
    if index < 0 or index >= len(chats):
        return jsonify({'error': 'Invalid chat index'}), 400
    chats.pop(index)
    new_index = len(chats) - 1
    session['chats'] = chats
    session['current_chat_index'] = new_index if new_index >= 0 else -1
    return jsonify({'success': True, 'chats': chats, 'current_index': session['current_chat_index']})

@app.route('/api/add_tag/<int:index>', methods=['POST'])
def add_tag(index):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    chats = session.get('chats', [])
    if index < 0 or index >= len(chats):
        return jsonify({'error': 'Invalid chat index'}), 400
    data = request.get_json() or {}
    tag = (data.get('tag') or '').strip()
    if not tag:
        return jsonify({'error': 'Tag cannot be empty'}), 400
    if 'tags' not in chats[index]:
        chats[index]['tags'] = []
    if tag not in chats[index]['tags']:
        chats[index]['tags'].append(tag)
    session['chats'] = chats
    return jsonify({'success': True, 'chats': chats})

@app.route('/api/remove_tag/<int:index>', methods=['POST'])
def remove_tag(index):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    chats = session.get('chats', [])
    if index < 0 or index >= len(chats):
        return jsonify({'error': 'Invalid chat index'}), 400
    data = request.get_json() or {}
    tag = (data.get('tag') or '').strip()
    if 'tags' in chats[index] and tag in chats[index]['tags']:
        chats[index]['tags'].remove(tag)
    session['chats'] = chats
    return jsonify({'success': True, 'chats': chats})

@app.route('/api/summarize_chat/<int:index>', methods=['POST'])
def summarize_chat(index):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    chats = session.get('chats', [])
    if index < 0 or index >= len(chats):
        return jsonify({'error': 'Invalid chat index'}), 400
    
    chat = chats[index]
    if not chat.get('messages'):
        return jsonify({'summary': 'No messages in this chat yet.'})
    
    messages_text = '\n'.join([
        f"{msg['type'].upper()}: {msg['message'][:200]}" 
        for msg in chat['messages']
    ])
    
    system_prompt = session.get('system_prompt', DEFAULT_SYSTEM_PROMPT)
    prompt_payload = f"System: {system_prompt}\n\nPlease provide a brief 1-2 sentence summary of this conversation:\n\n{messages_text}\n\nSummary:"
    
    payload = {
        "model": MODEL,
        "prompt": prompt_payload,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        response_data = response.json()
        summary = response_data.get('response', 'Unable to generate summary.')
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'summary': f'Error generating summary: {str(e)}'})

@app.route('/api/search_messages', methods=['POST'])
def search_messages():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json() or {}
    query = (data.get('query') or '').strip().lower()
    chats = session.get('chats', [])
    
    if not query:
        return jsonify({'results': []})
    
    results = []
    for chat_idx, chat in enumerate(chats):
        for msg_idx, msg in enumerate(chat.get('messages', [])):
            if query in msg.get('message', '').lower():
                results.append({
                    'chat_index': chat_idx,
                    'chat_title': chat.get('title', 'New Chat'),
                    'message_index': msg_idx,
                    'message': msg['message'][:300],
                    'type': msg['type']
                })
    
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)