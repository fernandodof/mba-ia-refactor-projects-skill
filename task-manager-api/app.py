import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from config.settings import SECRET_KEY, DATABASE_URL, DEBUG
from database import db
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.report_routes import report_bp
from middlewares.error_handler import register_error_handlers

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

CORS(app)
db.init_app(app)

app.register_blueprint(task_bp)
app.register_blueprint(user_bp)
app.register_blueprint(report_bp)
register_error_handlers(app)


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': str(datetime.datetime.now())})


@app.route('/')
def index():
    return jsonify({'message': 'Task Manager API', 'version': '1.0'})


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=DEBUG, host='127.0.0.1', port=5000)
