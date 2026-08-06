from flask import Flask, url_for, render_template
from routes.home import home_bp
from routes.cliente import cliente_bp
from routes.work import work_bp

app = Flask(__name__)

app.register_blueprint(home_bp)
app.register_blueprint(cliente_bp)
app.register_blueprint(work_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8283, debug=True, use_reloader=False)