import os
from flask import Flask, request, send_from_directory, redirect, url_for

app = Flask(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_full_path(directory):
    # Get the full path of the directory within the script directory
    return os.path.abspath(os.path.join(ROOT_DIR, directory))

def is_subdirectory(directory):
    # Check if the directory is a subdirectory of the script directory
    return os.path.commonpath([get_full_path(directory), ROOT_DIR]) == ROOT_DIR

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the uploaded file
        file = request.files['file']
        
        if file:
            # Get the current directory from the URL
            current_dir = request.args.get('dir', '')
            
            if not is_subdirectory(current_dir):
                # Redirect to the root directory if the current directory is outside the script directory
                return redirect(url_for('index'))
            
            # Save the file to the current directory
            file_path = os.path.join(get_full_path(current_dir), file.filename)
            file.save(file_path)
            return redirect(url_for('index', dir=current_dir))
    
    # Get the current directory from the URL
    current_dir = request.args.get('dir', '')
    
    if not is_subdirectory(current_dir):
        # Redirect to the root directory if the current directory is outside the script directory
        return redirect(url_for('index'))
    
    # Get the list of files and directories in the current directory
    items = os.listdir(get_full_path(current_dir))
    
    # Filter out hidden files and directories
    items = [item for item in items if not item.startswith('.')]
    
    # Separate files and directories
    files = [item for item in items if os.path.isfile(os.path.join(get_full_path(current_dir), item))]
    directories = [item for item in items if os.path.isdir(os.path.join(get_full_path(current_dir), item))]
    
    return f'''
        <html>
        <head>
            <title>File Server</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    font-family: Arial, sans-serif;
                    color: #333;
                    background-color: #fff;
                }}

                h1 {{
                    margin-bottom: 20px;
                }}

                ul {{
                    padding: 0;
                    list-style-type: none;
                }}

                li {{
                    margin-bottom: 10px;
                }}

                a {{
                    color: #007bff;
                    text-decoration: none;
                }}

                .upload-form {{
                    margin-top: 20px;
                }}

                @media (prefers-color-scheme: dark) {{
                    body {{
                        color: #eee;
                        background-color: #222;
                    }}

                    a {{
                        color: #4db2ff;
                    }}
                }}

                @media only screen and (max-width: 600px) {{
                    body {{
                        padding: 10px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>File Server</h1>
                <form class="upload-form" action="/" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" />
                    <input type="hidden" name="dir" value="{current_dir}" />
                    <input type="submit" value="Upload" />
                </form>
                <h2>Files:</h2>
                <ul class="file-list">
                    {"".join(f'<li><a href="/download/{os.path.join(current_dir, file)}">{file}</a></li>' for file in files)}
                </ul>
                <h2>Directories:</h2>
                <ul class="file-list">
                    {"".join(f'<li><a href="?dir={os.path.join(current_dir, directory)}">{directory}</a></li>' for directory in directories)}
                </ul>
            </div>
        </body>
        </html>
    '''

@app.route('/download/<path:filepath>')
def download(filepath):
    # Serve the file for download
    return send_from_directory(get_full_path(os.path.dirname(filepath)), os.path.basename(filepath), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
