import os


db_user = os.getenv('FLASK_DB_USER')
db_password = os.getenv('FLASK_DB_PASSWORD')
db_name = os.getenv('FLASK_DB_NAME')

SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{db_user}:{db_password}@localhost/{db_name}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
