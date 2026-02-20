"""
Hybrid VCS Web Application
Flask-based web interface for the Hybrid VCS system
"""

from flask import Flask, request, jsonify, render_template_string
import os
import sys
from hybrid_vcs_original import HybridVCS
from datetime import datetime

app = Flask(__name__)
vcs = HybridVCS()

# Simple HTML template for the web UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Hybrid VCS - Web Interface</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .repo-list {
            list-style: none;
            padding: 0;
        }
        .repo-item {
            background: #ecf0f1;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        .repo-item h3 {
            margin: 0 0 10px 0;
            color: #2c3e50;
        }
        .repo-meta {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover {
            background-color: #2980b9;
        }
        input[type="text"] {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 300px;
        }
        .api-docs {
            background: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .endpoint {
            background: white;
            padding: 10px;
            margin: 5px 0;
            border-left: 3px solid #ffc107;
        }
        code {
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <h1>🔄 Hybrid VCS - Version Control System</h1>
    
    <div class="container">
        <h2>Welcome to Hybrid VCS</h2>
        <p>A modern version control system combining centralized and distributed features.</p>
        <p><strong>Status:</strong> System is operational</p>
        <p><strong>Server Time:</strong> {{ server_time }}</p>
    </div>
    
    <div class="container">
        <h2>Repositories</h2>
        {% if repositories %}
        <ul class="repo-list">
            {% for repo in repositories %}
            <li class="repo-item">
                <h3>{{ repo.name }}</h3>
                <div class="repo-meta">
                    <span>📅 Created: {{ repo.created }}</span><br>
                    <span>🌿 Branches: {{ repo.branches|join(', ') }}</span><br>
                    <span>📝 Commits: {{ repo.commits }}</span>
                </div>
            </li>
            {% endfor %}
        </ul>
        {% else %}
        <p>No repositories yet. Create one using the API!</p>
        {% endif %}
    </div>
    
    <div class="container api-docs">
        <h2>API Endpoints</h2>
        <div class="endpoint">
            <strong>POST /api/init</strong> - Initialize a new repository<br>
            <code>{"name": "repo-name"}</code>
        </div>
        <div class="endpoint">
            <strong>POST /api/add</strong> - Add a file to staging<br>
            <code>{"repo": "repo-name", "file": "path", "content": "base64-encoded"}</code>
        </div>
        <div class="endpoint">
            <strong>POST /api/commit</strong> - Commit staged changes<br>
            <code>{"repo": "repo-name", "message": "commit message", "author": "name"}</code>
        </div>
        <div class="endpoint">
            <strong>GET /api/repos</strong> - List all repositories
        </div>
        <div class="endpoint">
            <strong>GET /api/history/:repo</strong> - Get commit history
        </div>
        <div class="endpoint">
            <strong>GET /api/status/:repo</strong> - Get repository status
        </div>
        <div class="endpoint">
            <strong>POST /api/branch</strong> - Create a new branch<br>
            <code>{"repo": "repo-name", "branch": "branch-name"}</code>
        </div>
        <div class="endpoint">
            <strong>POST /api/checkout</strong> - Switch branches<br>
            <code>{"repo": "repo-name", "branch": "branch-name"}</code>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Home page with repository list"""
    repos = vcs.list_repositories()
    return render_template_string(
        HTML_TEMPLATE,
        repositories=repos,
        server_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.route('/api/init', methods=['POST'])
def init_repository():
    """Initialize a new repository"""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Repository name required"}), 400
    
    result = vcs.init_repository(data['name'])
    return jsonify(result), 201 if 'success' in result else 400

@app.route('/api/add', methods=['POST'])
def add_file():
    """Add file to staging area"""
    data = request.get_json()
    required = ['repo', 'file', 'content']
    
    if not data or not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Decode content (assuming base64 or plain text)
    import base64
    try:
        content = base64.b64decode(data['content'])
    except:
        content = data['content'].encode('utf-8')
    
    result = vcs.add_file(data['repo'], data['file'], content)
    return jsonify(result), 200 if 'success' in result else 400

@app.route('/api/commit', methods=['POST'])
def commit():
    """Commit staged changes"""
    data = request.get_json()
    required = ['repo', 'message']
    
    if not data or not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400
    
    author = data.get('author', 'Anonymous')
    result = vcs.commit(data['repo'], data['message'], author)
    return jsonify(result), 200 if 'success' in result else 400

@app.route('/api/repos', methods=['GET'])
def list_repos():
    """List all repositories"""
    repos = vcs.list_repositories()
    return jsonify({"repositories": repos})

@app.route('/api/history/<repo_name>', methods=['GET'])
def get_history(repo_name):
    """Get commit history"""
    limit = request.args.get('limit', 10, type=int)
    result = vcs.get_history(repo_name, limit)
    return jsonify(result), 200 if 'error' not in result else 404

@app.route('/api/status/<repo_name>', methods=['GET'])
def get_status(repo_name):
    """Get repository status"""
    result = vcs.get_status(repo_name)
    return jsonify(result), 200 if 'error' not in result else 404

@app.route('/api/branch', methods=['POST'])
def create_branch():
    """Create a new branch"""
    data = request.get_json()
    required = ['repo', 'branch']
    
    if not data or not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400
    
    result = vcs.create_branch(data['repo'], data['branch'])
    return jsonify(result), 201 if 'success' in result else 400

@app.route('/api/checkout', methods=['POST'])
def checkout():
    """Switch branches"""
    data = request.get_json()
    required = ['repo', 'branch']
    
    if not data or not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400
    
    result = vcs.checkout(data['repo'], data['branch'])
    return jsonify(result), 200 if 'success' in result else 400

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Hybrid VCS",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

def main():
    """Main entry point"""
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Hybrid VCS Server on port {port}...")
    print(f"Access the web interface at: http://localhost:{port}/")
    print(f"API documentation available at: http://localhost:{port}/")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == '__main__':
    main()
