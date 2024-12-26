from flask import Flask
from config import Config
import openai
from db_setup import execute_sql_file

def create_app():#Application factory pattern.
    app = Flask(__name__)#Creates an instance of the application.
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
    execute_sql_file("path/to/sql/script")

    openai.api_key = app.config['OPENAI_API_KEY']#Enables API functionality.

    with app.app_context():
        from .routes import register_routes
        register_routes(app)
    
    

    return app

app = create_app()

#Boilerplate Flask code
#execute_sql_file should contain the directory of the SQL file to be executed on the PC running the system.
#A path to the SQL file was given a variable name in config.py, however the system was unable to use this, hence why the route is hard coded here instead.
