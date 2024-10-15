from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Path to the file where emails will be stored
EMAIL_FILE_PATH = 'emails.txt'

# Predefined secret key for validation
SECRET_KEY = 'JJHajfnoieBJKdsknaJ^ksjflKSDKf33m#$$hadbfk'

def email_exists(email):
    """Check if the email already exists in the file."""
    try:
        with open(EMAIL_FILE_PATH, 'r') as file:
            for line in file:
                if line.strip() == email:
                    return True
    except FileNotFoundError:
        # If the file does not exist, return False
        return False
    return False

@app.route('/')
@app.route('/home')
@app.route('/newsletter')
def index():
    return render_template('main.html')

@app.route('/latest')
def latest():
    return render_template('latest.html')

@app.route('/blog')
@app.route('/blogs')
def blog():
    # Specify the folder path
    folder_path = 'templates/blogs'

    # Get a list of all files in the 'templates/blogs' folder
    blog_posts = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    print(blog_posts)
    # Pass the blog_posts list to the template
    return render_template('blog.html', blog_posts=blog_posts)

@app.route('/blog/<filename>')
def render_blog(filename):
    print(filename)
    return render_template(f'blogs/{filename}')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form['email']
    if email:
        if email_exists(email):
            return jsonify({'message': 'This email is already subscribed.'}), 400
        with open(EMAIL_FILE_PATH, 'a') as file:
            file.write(email + '\n')
        return jsonify({'message': 'Thank you for subscribing!'})
    return jsonify({'message': 'Failed to subscribe. Please try again.'}), 400

# New API endpoint to accept an HTML file with secret key validation and destination selection
@app.route('/upload_html', methods=['POST'])
def upload_html():
    secret_key = request.headers.get('Secret-Key')
    destination = request.form.get('type')  # 'blog' or 'email'

    # Validate the secret key
    if secret_key != SECRET_KEY:
        return jsonify({'error': 'Invalid secret key'}), 403

    # Validate destination type
    if destination not in ['blog', 'email']:
        return jsonify({'error': 'Invalid destination type. Must be "blog" or "email".'}), 400

    # Check if the file part is present in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']

    # Ensure the file is an HTML file
    if file.filename == '' or not file.filename.endswith('.html'):
        return jsonify({'error': 'No HTML file selected or incorrect file type'}), 400

    # Set the appropriate directory based on the type
    if destination == 'blog':
        save_path = os.path.join('templates', 'blogs', file.filename)
    elif destination == 'email':
        save_path = os.path.join('DATA', 'output.html')

    # Ensure the directory exists before saving
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Save the file to the appropriate folder
    file.save(save_path)

    return jsonify({'message': f'File {file.filename} uploaded successfully to {destination}.'}), 200



@app.route('/emails', methods=['GET'])
def get_emails():
    """Return all emails from emails.txt as JSON."""
    secret_key = request.headers.get('Secret-Key')  # Get the secret key from the headers

    # Validate the secret key
    if secret_key != SECRET_KEY:
        return jsonify({'error': 'Invalid secret key'}), 403

    try:
        with open(EMAIL_FILE_PATH, 'r') as file:
            emails = [line.strip() for line in file if line.strip()]  # Read and strip lines
        return jsonify(emails), 200  # Return the list of emails as JSON
    except FileNotFoundError:
        return jsonify({'error': 'Email file not found'}), 404

@app.route("/ricochet_radio")
def ricochet():
    return render_template('ricochet_radio.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
