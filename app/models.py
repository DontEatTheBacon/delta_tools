from typing import List, Optional

import sqlalchemy as sa
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login

association_table = sa.Table(
    'association_table',
    db.metadata,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('section_id', sa.Integer, sa.ForeignKey('section.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(32), unique=True, index=True)
    email: Mapped[str] = mapped_column(sa.String(32), unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(sa.String(256))

    watching: Mapped[List['Section']] = relationship(
        secondary=association_table,
        back_populates='watchlist'
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Section(db.Model):
    __tablename__ = 'section'
    id: Mapped[int] = mapped_column(primary_key=True)
    watchlist: Mapped[List[User]] = relationship(
        secondary=association_table,
        back_populates='watching'
    )

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))