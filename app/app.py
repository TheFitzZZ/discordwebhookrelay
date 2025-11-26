import os
import yaml
import requests
import uuid
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(24)

CONFIG_DIR = os.environ.get('CONFIG_DIR', './config')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.yaml')

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {'endpoints': []}
    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f) or {'endpoints': []}

def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f)

@app.route('/')
def index():
    return redirect(url_for('admin'))

@app.route('/admin')
def admin():
    config = load_config()
    return render_template('index.html', endpoints=config.get('endpoints', []))

@app.route('/admin/add', methods=['POST'])
def add_endpoint():
    config = load_config()
    name = request.form.get('name')
    msg_type = request.form.get('type')
    discord_url = request.form.get('discord_url')
    
    if not name or not discord_url:
        flash('Name and Discord URL are required')
        return redirect(url_for('admin'))

    new_endpoint = {
        'id': str(uuid.uuid4()),
        'name': name,
        'type': msg_type,
        'discord_url': discord_url
    }
    
    if 'endpoints' not in config:
        config['endpoints'] = []
        
    config['endpoints'].append(new_endpoint)
    save_config(config)
    return redirect(url_for('admin'))

@app.route('/admin/delete/<endpoint_id>')
def delete_endpoint(endpoint_id):
    config = load_config()
    config['endpoints'] = [e for e in config.get('endpoints', []) if e['id'] != endpoint_id]
    save_config(config)
    return redirect(url_for('admin'))

@app.route('/webhook/<endpoint_id>', methods=['POST'])
def webhook(endpoint_id):
    config = load_config()
    endpoint = next((e for e in config.get('endpoints', []) if e['id'] == endpoint_id), None)
    
    if not endpoint:
        return jsonify({'error': 'Endpoint not found'}), 404

    # Get content from request
    content = request.data.decode('utf-8')
    
    # If content is empty, try form data or json
    if not content:
        if request.is_json:
            content = str(request.json)
        else:
            content = str(request.form.to_dict())

    # Format for Discord
    discord_payload = {}
    
    final_message = f"**Notification from {endpoint['name']}**\n"
    
    if endpoint['type'] == 'html':
        # Very basic HTML stripping/conversion
        content = content.replace('<br>', '\n').replace('<br/>', '\n')
        # Remove other tags (simple regex or just leave them if they are readable)
        import re
        clean = re.compile('<.*?>')
        content = re.sub(clean, '', content)
        final_message += content
    else:
        final_message += content

    # Discord has a 2000 char limit. Truncate if necessary or split?
    # For simplicity, truncate.
    if len(final_message) > 1900:
        final_message = final_message[:1900] + "...(truncated)"

    discord_payload = {
        "content": final_message
    }

    try:
        resp = requests.post(endpoint['discord_url'], json=discord_payload)
        resp.raise_for_status()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
