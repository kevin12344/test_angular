from flask import Flask
from blueprints.login.api import bp_main as login_api
from flask_cors import CORS
import os


app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})

app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.register_blueprint(login_api, url_prefix='/login/api')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run('0.0.0.0', port=port)
