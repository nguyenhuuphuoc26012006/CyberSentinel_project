import json
import os
import redis
from flask import Blueprint, jsonify, request
from sqlalchemy import desc, text
from .extensions import db
from .models import Alert, SecurityEvent
from .detection import evaluate_event

api_bp = Blueprint("api", __name__)

def get_redis():
    return redis.Redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        decode_responses=True,
        socket_connect_timeout=1,
    )

@api_bp.get("/health")
def health():
    result = {"status": "ok", "service": "CyberSentinel API"}
    try:
        db.session.execute(text("SELECT 1"))
        result["database"] = "ok"
    except Exception:
        db.session.rollback()
        result["database"] = "error"
        result["status"] = "degraded"
    try:
        get_redis().ping()
        result["redis"] = "ok"
    except Exception:
        result["redis"] = "error"
        result["status"] = "degraded"
    return jsonify(result), (200 if result["status"] == "ok" else 503)

@api_bp.post("/events")
def ingest_event():
    data = request.get_json(silent=True) or {}
    required = ["event_type"]
    missing = [field for field in required if not data.get(field)]
    if missing:
        return jsonify({"error": "Missing required fields", "fields": missing}), 400

    allowed_severities = {"info", "low", "medium", "high", "critical"}
    severity = str(data.get("severity", "low")).lower()
    if severity not in allowed_severities:
        return jsonify({"error": "Invalid severity"}), 400

    event = SecurityEvent(
        source=str(data.get("source", "unknown"))[:100],
        event_type=str(data["event_type"])[:100],
        source_ip=(str(data["source_ip"])[:45] if data.get("source_ip") else None),
        username=(str(data["username"])[:120] if data.get("username") else None),
        severity=severity,
        message=(str(data["message"])[:4000] if data.get("message") else None),
    )
    db.session.add(event)
    db.session.flush()

    alert = evaluate_event(event)
    db.session.commit()

    payload = {"event": event.to_dict(), "alert": alert.to_dict() if alert else None}
    try:
        get_redis().xadd("cybersentinel:events", {"payload": json.dumps(payload)}, maxlen=10000, approximate=True)
    except Exception:
        # PostgreSQL remains the source of truth in this starter implementation.
        pass

    return jsonify(payload), 201

@api_bp.get("/events")
def list_events():
    limit = request.args.get("limit", default=50, type=int)
    limit = max(1, min(limit, 200))
    query = SecurityEvent.query.order_by(desc(SecurityEvent.created_at)).limit(limit)
    return jsonify({"items": [item.to_dict() for item in query.all()], "limit": limit})

@api_bp.get("/alerts")
def list_alerts():
    limit = request.args.get("limit", default=50, type=int)
    limit = max(1, min(limit, 200))
    query = Alert.query.order_by(desc(Alert.created_at)).limit(limit)
    return jsonify({"items": [item.to_dict() for item in query.all()], "limit": limit})
