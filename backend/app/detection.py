
import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from .extensions import db
from .models import Alert, SecurityEvent


BRUTE_FORCE_THRESHOLD = int(
    os.getenv("BRUTE_FORCE_THRESHOLD", "5")
)

BRUTE_FORCE_WINDOW_SECONDS = int(
    os.getenv("BRUTE_FORCE_WINDOW_SECONDS", "300")
)


def evaluate_event(event: SecurityEvent):
    """
    Detect repeated failed login attempts from one source IP.
    Rule ID: AUTH-001
    """

    if event.event_type != "login_failure" or not event.source_ip:
        return None

    cutoff = datetime.now(timezone.utc) - timedelta(
        seconds=BRUTE_FORCE_WINDOW_SECONDS
    )

    count = (
        db.session.query(func.count(SecurityEvent.id))
        .filter(
            SecurityEvent.event_type == "login_failure",
            SecurityEvent.source_ip == event.source_ip,
            SecurityEvent.created_at >= cutoff,
        )
        .scalar()
    )

    if count < BRUTE_FORCE_THRESHOLD:
        return None

    # Prevent duplicate open alerts for the same IP.
    existing = Alert.query.filter_by(
        rule_id="AUTH-001",
        source_ip=event.source_ip,
        status="open",
    ).first()

    if existing:
        return existing

    alert = Alert(
        title="Possible Brute Force Activity",
        rule_id="AUTH-001",
        severity="high",
        source_ip=event.source_ip,
        description=(
            f"{count} failed login events from "
            f"{event.source_ip} within "
            f"{BRUTE_FORCE_WINDOW_SECONDS} seconds."
        ),
    )

    db.session.add(alert)
    db.session.flush()

    return alert
