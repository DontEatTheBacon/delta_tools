import sqlalchemy as sa

from app import create_app, db
from app.models import User

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'sa': sa, 'User': User}