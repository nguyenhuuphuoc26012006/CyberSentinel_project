from datetime import datetime, timezone
from .extensions import db

def utcnow():
    return datetime.now(timezone.utc)

class SecurityEvent(db.Model):
    __tablename__ = "security_events"

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False, default="unknown")
    event_type = db.Column(db.String(100), nullable=False)
    source_ip = db.Column(db.String(45), nullable=True, index=True)
    username = db.Column(db.String(120), nullable=True)
    severity = db.Column(db.String(20), nullable=False, default="low")
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "source": self.source,
            "event_type": self.event_type,
            "source_ip": self.source_ip,
            "username": self.username,
            "severity": self.severity,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
        }

class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    rule_id = db.Column(db.String(100), nullable=False, index=True)
    severity = db.Column(db.String(20), nullable=False)
    source_ip = db.Column(db.String(45), nullable=True, index=True)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="open")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "rule_id": self.rule_id,
            "severity": self.severity,
            "source_ip": self.source_ip,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
