from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="notifications.tasks.send_notification_async",
)
def send_notification_async(self, notification_id: int) -> bool:
    """
    Asynchronously dispatch a single staged notification entry.
    Retries up to 3 times with Celery back-off if an unexpected system crash happens.
    """
    try:
        from notifications.services.notification_service import NotificationService
        
        success = NotificationService.dispatch_now(notification_id)
        if not success:
            logger.warning("Notification #%d dispatch returned failure.", notification_id)
        return success
    except Exception as exc:
        logger.error("Failed to run send_notification_async task: notification_id=%s, error=%s", notification_id, exc)
        raise self.retry(exc=exc, countdown=60)


@shared_task(name="notifications.tasks.process_pending_notifications_cron")
def process_pending_notifications_cron() -> dict:
    """
    Periodic task: Sweeps and processes all stuck PENDING notifications.
    Can be scheduled via Celery beat.
    """
    from notifications.providers.notification_provider import NotificationProvider
    from notifications.services.notification_service import NotificationService

    pending = NotificationProvider.get_notification()._notification_repo().get_pending_notifications(limit=100)
    
    processed_count = 0
    success_count = 0
    for entity in pending:
        try:
            success = NotificationService.dispatch_now(entity.id)  # type: ignore
            processed_count += 1
            if success:
                success_count += 1
        except Exception as exc:
            logger.error("Error processing pending notification #%s: %s", entity.id, exc)

    logger.info("Sweeper completed: processed %d, succeeded %d", processed_count, success_count)
    return {"processed": processed_count, "success": success_count}
