from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy.dialects.sqlite import JSON  # for issues list
from flask_login import UserMixin
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()

# --- Enable SQLite foreign keys ---
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class User(db.Model, UserMixin):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    # Relationships
    jobs = db.relationship("Job", backref="user", lazy=True, cascade="all, delete-orphan")
    uploads = db.relationship("Upload", backref="user", lazy=True, cascade="all, delete-orphan")


class Job(db.Model):
    __tablename__ = "jobs"
    
    id = db.Column(db.String, primary_key=True)  # UUID or custom ID
    case_number = db.Column(db.String, nullable=False)
    branch = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    status = db.Column(db.String, nullable=False)
    created_at = db.Column(
    db.DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc)
)
    feature = db.Column(db.String, nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Relationships
    uploads = db.relationship("Upload", backref="job", lazy=True, cascade="all, delete-orphan")
    audit_result = db.relationship("AuditResult", backref="job", uselist=False, lazy=True, cascade="all, delete-orphan")


class AuditResult(db.Model):
    __tablename__ = "audit_results"
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String, db.ForeignKey("jobs.id"), nullable=False)
    
    accuracy = db.Column(db.String, nullable=True)   
    issues = db.Column(JSON, nullable=True)         
    completed_at = db.Column(
    db.DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc)
)
    error = db.Column(db.Text, nullable=True)


class Upload(db.Model):
    __tablename__ = "uploads"
    
    id = db.Column(db.Integer, primary_key=True)
    permanent_file_name = db.Column(db.String, nullable=False)
    file_path = db.Column(db.String, nullable=False)
    
    job_id = db.Column(db.String, db.ForeignKey("jobs.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
