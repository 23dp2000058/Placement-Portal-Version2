from flask_sqlalchemy import SQLAlchemy
from flask_security import Security

db = SQLAlchemy()
security = Security()

from flask_migrate import Migrate
migrate = Migrate()