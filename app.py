import os
from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from extensions import db, mail, login_manager, csrf
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    from routes import routes_bp
    from auth import auth_bp
    from admin import admin_bp
    from notifications import notifications_bp
    
    app.register_blueprint(routes_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notifications_bp)
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('error.html', 
                             error_code=403, 
                             error_message='Access Forbidden',
                             error_description='You do not have permission to access this page.'), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error.html', 
                             error_code=404, 
                             error_message='Page Not Found',
                             error_description='The page you are looking for does not exist.'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', 
                             error_code=500, 
                             error_message='Internal Server Error',
                             error_description='Something went wrong on our end. Please try again later.'), 500
    
    @app.errorhandler(413)
    def too_large_error(error):
        return render_template('error.html', 
                             error_code=413, 
                             error_message='File Too Large',
                             error_description='The uploaded file exceeds the maximum allowed size.'), 413
    
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)