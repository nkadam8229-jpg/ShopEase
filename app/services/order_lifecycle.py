"""
Automatic order lifecycle processor.

Orders created by ShopEase are simulated through:
    0:00  PENDING
    0:30  CONFIRMED
    2:30  SHIPPED
    4:30  DELIVERED

This processor runs independently of customer page visits so an order
continues through its lifecycle even when nobody logs in or opens the
order page.
"""

import logging
import threading
import time
from datetime import datetime

from app import db
from app.models import Order


logger = logging.getLogger(__name__)

# Keep this short enough for the simulated lifecycle to be updated promptly.
PROCESS_INTERVAL_SECONDS = 5

# Only these statuses are controlled by the automatic simulation.
# CANCELLED (and any future manually-managed status) is never overwritten.
AUTO_STATUSES = ("PENDING", "CONFIRMED", "SHIPPED")


def _status_for_elapsed_seconds(elapsed_seconds):
    """Return the simulated status for an order's age."""
    if elapsed_seconds >= 270:
        return "DELIVERED"
    if elapsed_seconds >= 150:
        return "SHIPPED"
    if elapsed_seconds >= 30:
        return "CONFIRMED"
    return "PENDING"


def process_order_lifecycle(app):
    """
    Update eligible orders based on their created_at timestamp.

    This function is safe to call repeatedly. It commits only when an
    order's status actually needs to advance.
    """
    with app.app_context():
        try:
            now = datetime.utcnow()

            orders = (
                Order.query
                .filter(Order.status.in_(AUTO_STATUSES))
                .all()
            )

            changed = 0

            for order in orders:
                if not order.created_at:
                    continue

                elapsed = (now - order.created_at).total_seconds()
                target_status = _status_for_elapsed_seconds(elapsed)

                # Never move an order backwards.
                progression = {
                    "PENDING": 0,
                    "CONFIRMED": 1,
                    "SHIPPED": 2,
                    "DELIVERED": 3,
                }

                current_rank = progression.get(order.status, -1)
                target_rank = progression.get(target_status, -1)

                if target_rank > current_rank:
                    order.status = target_status
                    changed += 1

            if changed:
                db.session.commit()
                logger.info(
                    "Automatic order lifecycle: advanced %s order(s).",
                    changed,
                )

        except Exception:
            db.session.rollback()
            logger.exception("Automatic order lifecycle update failed.")


def _worker(app):
    """Background worker loop."""
    while True:
        try:
            process_order_lifecycle(app)
        except Exception:
            logger.exception("Order lifecycle worker iteration failed.")

        time.sleep(PROCESS_INTERVAL_SECONDS)


def start_order_lifecycle_worker(app):
    """
    Start one daemon worker for this Flask process.

    The worker is intentionally a daemon so it never prevents the Flask
    process from shutting down.
    """
    # Avoid duplicate workers when Flask's development reloader creates
    # a parent process and a serving child process.
    if app.debug and app.config.get("WERKZEUG_RUN_MAIN") != "true":
        return None

    worker = threading.Thread(
        target=_worker,
        args=(app,),
        name="order-lifecycle-worker",
        daemon=True,
    )
    worker.start()

    logger.info(
        "Automatic order lifecycle worker started "
        "(interval=%ss).",
        PROCESS_INTERVAL_SECONDS,
    )

    return worker

