from flask import Flask, render_template
from api.routes import api_bp
from api.storage import clean_stale_data

app = Flask(__name__)

# Register API blueprint
app.register_blueprint(api_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    clean_stale_data()
    app.run(host='0.0.0.0', port=5000, debug=True)