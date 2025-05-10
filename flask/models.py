"""models.py - SQLAlchemy models for Flask app."""

from . import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    agents = db.relationship('Agent', back_populates='team', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Team {self.name}>"

class Agent(db.Model):
    __tablename__ = 'agents'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(64), nullable=True)
    description = db.Column(db.Text, nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    team = db.relationship('Team', back_populates='agents')

    def __repr__(self):
        return f"<Agent {self.name} ({self.role})>"