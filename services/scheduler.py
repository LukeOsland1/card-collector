"""Background job scheduler for card expiry and maintenance tasks."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from db.base import get_db
from db.crud import CardInstanceCRUD, AuditLogCRUD, UserCRUD
from db.models import CardInstance

logger = logging.getLogger(__name__)


class CardExpiryScheduler:
    """Background scheduler for card expiry and maintenance tasks."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """Setup scheduled jobs."""
        
        # Check for expired cards every 5 minutes
        self.scheduler.add_job(
            self.process_expired_cards,
            trigger=IntervalTrigger(minutes=5),
            id="process_expired_cards",
            name="Process Expired Cards",
            replace_existing=True,
        )
        
        # Send expiry warnings every hour
        self.scheduler.add_job(
            self.send_expiry_warnings,
            trigger=IntervalTrigger(hours=1),
            id="send_expiry_warnings",
            name="Send Expiry Warnings",
            replace_existing=True,
        )
        
        # Clean up old audit logs daily at 2 AM
        self.scheduler.add_job(
            self.cleanup_audit_logs,
            trigger=CronTrigger(hour=2, minute=0),
            id="cleanup_audit_logs",
            name="Cleanup Old Audit Logs",
            replace_existing=True,
        )
        
        # Update user activity stats daily at 3 AM
        self.scheduler.add_job(
            self.update_user_stats,
            trigger=CronTrigger(hour=3, minute=0),
            id="update_user_stats",
            name="Update User Activity Stats",
            replace_existing=True,
        )
        
        # Send weekly reports on Sundays at 9 AM
        self.scheduler.add_job(
            self.send_weekly_reports,
            trigger=CronTrigger(day_of_week=6, hour=9, minute=0),
            id="send_weekly_reports",
            name="Send Weekly Reports",
            replace_existing=True,
        )
    
    async def start(self):
        """Start the scheduler."""
        try:
            self.scheduler.start()
            logger.info("Background scheduler started")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    async def stop(self):
        """Stop the scheduler."""
        try:
            self.scheduler.shutdown(wait=True)
            logger.info("Background scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    async def process_expired_cards(self):
        """Process expired card instances."""
        try:
            async for db in get_db():
                expired_instances = await CardInstanceCRUD.get_expired_instances(db)
                
                if not expired_instances:
                    return
                
                logger.info(f"Processing {len(expired_instances)} expired card instances")
                
                for instance in expired_instances:
                    try:
                        # Mark as removed
                        await CardInstanceCRUD.remove(db, instance.id, None)  # System removal
                        
                        # Log the expiry
                        await AuditLogCRUD.create(
                            db,
                            actor_user_id=0,  # System actor
                            action="card_instance_expired",
                            target_type="card_instance",
                            target_id=instance.id,
                            meta={
                                "card_name": instance.card.name,
                                "owner_id": instance.owner_user_id,
                                "expired_at": instance.expires_at.isoformat() if instance.expires_at else None,
                                "auto_removed": True,
                            }
                        )
                        
                        logger.info(f"Expired card instance {instance.id} for user {instance.owner_user_id}")
                        
                    except Exception as e:
                        logger.error(f"Error processing expired instance {instance.id}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error in process_expired_cards: {e}")
    
    async def send_expiry_warnings(self):
        """Send warnings for cards expiring soon."""
        try:
            # This would send Discord notifications to users
            # For now, we'll just log the warnings
            
            async for db in get_db():
                # Find cards expiring in the next 24 hours
                warning_time = datetime.utcnow() + timedelta(hours=24)
                
                # Query would be more complex in real implementation
                # This is a simplified version
                result = await db.execute(
                    """
                    SELECT ci.id, ci.owner_user_id, ci.expires_at, c.name
                    FROM card_instances ci
                    JOIN cards c ON ci.card_id = c.id
                    WHERE ci.expires_at <= ?
                    AND ci.expires_at > ?
                    AND ci.removed_at IS NULL
                    """,
                    (warning_time, datetime.utcnow())
                )
                
                expiring_soon = result.fetchall()
                
                if expiring_soon:
                    logger.info(f"Found {len(expiring_soon)} cards expiring within 24 hours")
                    
                    for instance_id, user_id, expires_at, card_name in expiring_soon:
                        # In real implementation, this would send a Discord DM
                        logger.info(
                            f"Warning: Card '{card_name}' for user {user_id} "
                            f"expires at {expires_at}"
                        )
                        
                        # Log the warning
                        await AuditLogCRUD.create(
                            db,
                            actor_user_id=0,
                            action="card_expiry_warning_sent",
                            target_type="card_instance",
                            target_id=instance_id,
                            meta={
                                "card_name": card_name,
                                "owner_id": user_id,
                                "expires_at": expires_at.isoformat(),
                                "warning_type": "24_hour",
                            }
                        )
                        
        except Exception as e:
            logger.error(f"Error in send_expiry_warnings: {e}")
    
    async def cleanup_audit_logs(self):
        """Clean up old audit logs."""
        try:
            async for db in get_db():
                # Keep logs for 90 days by default
                cleaned_count = await AuditLogCRUD.cleanup_old_logs(db, days=90)
                
                if cleaned_count > 0:
                    logger.info(f"Cleaned up {cleaned_count} old audit log entries")
                    
        except Exception as e:
            logger.error(f"Error in cleanup_audit_logs: {e}")
    
    async def update_user_stats(self):
        """Update user activity statistics."""
        try:
            async for db in get_db():
                # Update last activity for users
                active_users = await UserCRUD.get_active_users(db, days=7)
                
                logger.info(f"Found {len(active_users)} active users in the last 7 days")
                
                # You could update additional statistics here
                # like card collection counts, rarity distributions, etc.
                
        except Exception as e:
            logger.error(f"Error in update_user_stats: {e}")
    
    async def send_weekly_reports(self):
        """Send weekly activity reports."""
        try:
            async for db in get_db():
                # Generate weekly statistics
                now = datetime.utcnow()
                week_ago = now - timedelta(days=7)
                
                # Get recent audit logs for the report
                recent_logs = await AuditLogCRUD.get_recent_actions(
                    db, limit=1000, days=7
                )
                
                # Calculate statistics
                stats = self._calculate_weekly_stats(recent_logs)
                
                logger.info(f"Weekly report: {stats}")
                
                # In real implementation, this would send reports to admin channels
                
        except Exception as e:
            logger.error(f"Error in send_weekly_reports: {e}")
    
    def _calculate_weekly_stats(self, audit_logs: List) -> dict:
        """Calculate weekly statistics from audit logs."""
        stats = {
            "total_actions": len(audit_logs),
            "cards_created": 0,
            "cards_approved": 0,
            "cards_rejected": 0,
            "instances_assigned": 0,
            "instances_expired": 0,
            "unique_users": set(),
        }
        
        for log in audit_logs:
            stats["unique_users"].add(log.actor_user_id)
            
            if log.action == "card_created":
                stats["cards_created"] += 1
            elif log.action == "card_approved":
                stats["cards_approved"] += 1
            elif log.action == "card_rejected":
                stats["cards_rejected"] += 1
            elif log.action == "card_assigned":
                stats["instances_assigned"] += 1
            elif log.action == "card_instance_expired":
                stats["instances_expired"] += 1
        
        stats["unique_users"] = len(stats["unique_users"])
        
        return stats
    
    def add_custom_job(
        self,
        func,
        trigger,
        job_id: str,
        name: str = None,
        **kwargs
    ):
        """Add a custom scheduled job."""
        self.scheduler.add_job(
            func=func,
            trigger=trigger,
            id=job_id,
            name=name or job_id,
            replace_existing=True,
            **kwargs
        )
    
    def remove_job(self, job_id: str):
        """Remove a scheduled job."""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job: {job_id}")
        except Exception as e:
            logger.error(f"Error removing job {job_id}: {e}")
    
    def get_job_status(self) -> dict:
        """Get status of all scheduled jobs."""
        jobs = self.scheduler.get_jobs()
        
        return {
            "scheduler_running": self.scheduler.running,
            "total_jobs": len(jobs),
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger),
                }
                for job in jobs
            ]
        }


class MaintenanceScheduler:
    """Additional maintenance tasks scheduler."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    async def start(self):
        """Start maintenance scheduler."""
        # Add maintenance jobs here
        # Examples: database optimization, image cleanup, etc.
        
        self.scheduler.add_job(
            self.database_maintenance,
            trigger=CronTrigger(day_of_week=0, hour=4, minute=0),  # Sunday 4 AM
            id="database_maintenance",
            name="Database Maintenance",
            replace_existing=True,
        )
        
        self.scheduler.start()
        logger.info("Maintenance scheduler started")
    
    async def stop(self):
        """Stop maintenance scheduler."""
        self.scheduler.shutdown(wait=True)
        logger.info("Maintenance scheduler stopped")
    
    async def database_maintenance(self):
        """Perform database maintenance tasks."""
        try:
            async for db in get_db():
                # Example maintenance tasks:
                # - Analyze tables for query optimization
                # - Clean up orphaned records
                # - Update statistics
                
                logger.info("Running database maintenance tasks")
                
                # You could add specific database maintenance queries here
                
        except Exception as e:
            logger.error(f"Error in database_maintenance: {e}")


# Global scheduler instances
card_expiry_scheduler = CardExpiryScheduler()
maintenance_scheduler = MaintenanceScheduler()


async def start_schedulers():
    """Start all background schedulers."""
    try:
        await card_expiry_scheduler.start()
        await maintenance_scheduler.start()
        logger.info("All schedulers started successfully")
    except Exception as e:
        logger.error(f"Error starting schedulers: {e}")
        raise


async def stop_schedulers():
    """Stop all background schedulers."""
    try:
        await card_expiry_scheduler.stop()
        await maintenance_scheduler.stop()
        logger.info("All schedulers stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping schedulers: {e}")


async def get_scheduler_status():
    """Get status of all schedulers."""
    return {
        "card_expiry_scheduler": card_expiry_scheduler.get_job_status(),
        "maintenance_scheduler": {
            "scheduler_running": maintenance_scheduler.scheduler.running,
            "total_jobs": len(maintenance_scheduler.scheduler.get_jobs()),
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger),
                }
                for job in maintenance_scheduler.scheduler.get_jobs()
            ]
        }
    }