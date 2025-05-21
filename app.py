from flask import Flask
from modules.routes.main_routes import configure_routes

# Create the Flask application
app = Flask(__name__)

# Configure routes
configure_routes(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 