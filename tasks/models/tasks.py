# ============================================================================
# FILE: apps/tasks/models.py (Enhanced)
# Enhanced Task Models with Entity Linking
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q
from datetime import timedelta
from tenants.models.tenants import Tenant


class Task(models.Model):
    """
    Enhanced task model with comprehensive tracking
    
    Features:
    - Multi-tenant support: Each tenant has own tasks
    - Task lists: Organize tasks in lists
    - Priority levels: LOW, MEDIUM, HIGH, URGENT
    - Status tracking: TODO, IN_PROGRESS, REVIEW, DONE, CANCELLED
    - Assignment: Assign to users
    - Due dates: Set deadlines
    - Entity linking: Link to trips, vehicles, bookings, etc.
    - Completion tracking: Track when completed
    - Audit trail: Track creator and updates
    - Bulk operations: Batch update tasks
    - Advanced filtering: Query by multiple criteria
    
    Status Flow:
    TODO -> IN_PROGRESS -> REVIEW -> DONE
    TODO -> CANCELLED
    IN_PROGRESS -> CANCELLED
    REVIEW -> CANCELLED
    
    Priority Levels:
    - LOW: Can be done anytime
    - MEDIUM: Regular priority (default)
    - HIGH: Important task
    - URGENT: Must be done immediately
    
    Entity Types:
    - trips: Trip-related tasks
    - vehicles: Vehicle-related tasks
    - bookings: Booking-related tasks
    - employees: Employee-related tasks
    - invoices: Invoice-related tasks
    - documents: Document-related tasks
    - custom: Custom entity types
    
    Example:
        # Create task
        task = Task.objects.create(
            tenant=tenant,
            title='Inspect vehicle',
            priority='HIGH',
            status='TODO',
            assignee=user,
            entity_type='vehicles',
            entity_id=vehicle.id
        )
        
        # Update status
        task.move_to_in_progress()
        task.move_to_review()
        task.mark_done()
        
        # Get tasks
        tasks = Task.get_user_tasks(user)
        overdue = Task.get_overdue_tasks()
    """

    PRIORITY_CHOICES = (
        ('LOW', _('Low - Can be done anytime')),
        ('MEDIUM', _('Medium - Regular priority')),
        ('HIGH', _('High - Important task')),
        ('URGENT', _('Urgent - Must be done immediately')),
    )

    STATUS_CHOICES = (
        ('TODO', _('To Do - Not started')),
        ('IN_PROGRESS', _('In Progress - Currently being worked on')),
        ('REVIEW', _('Review - Waiting for review')),
        ('DONE', _('Done - Task completed')),
        ('CANCELLED', _('Cancelled - Task cancelled')),
    )

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='tasks',
        db_index=True,
        help_text='Tenant that owns this task'
    )
    
    # ========================================================================
    # TASK LIST RELATIONSHIP
    # ========================================================================
    
    list = models.ForeignKey(
        'TaskList',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        db_index=True,
        help_text='Task list this task belongs to'
    )
    
    # ========================================================================
    # TASK INFORMATION
    # ========================================================================
    
    title = models.CharField(
        max_length=500,
        help_text='Task title'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Detailed task description'
    )
    
    # ========================================================================
    # PRIORITY AND STATUS
    # ========================================================================
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        db_index=True,
        help_text='Task priority'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='TODO',
        db_index=True,
        help_text='Task status'
    )
    
    # ========================================================================
    # ASSIGNMENT
    # ========================================================================
    
    assignee = models.ForeignKey(
        'accounts.UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        db_index=True,
        help_text='User this task is assigned to'
    )
    
    # ========================================================================
    # AUDIT INFORMATION
    # ========================================================================
    
    created_by = models.ForeignKey(
        'accounts.UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_created',
        help_text='User who created this task'
    )
    
    # ========================================================================
    # DATES
    # ========================================================================
    
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text='Due date for task'
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When task was completed'
    )
    
    # ========================================================================
    # ENTITY LINKING
    # ========================================================================
    
    entity_type = models.CharField(
        max_length=60,
        null=True,
        blank=True,
        db_index=True,
        help_text='Type of entity this task is linked to'
    )
    
    entity_id = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text='ID of entity this task is linked to'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When task was created'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When task was last updated'
    )

    class Meta:
        db_table = 'tasks'
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
        ordering = ['-priority', 'due_date', '-created_at']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Priority constraint
            models.CheckConstraint(
                check=Q(priority__in=['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
                name='chk_task_priority',
                violation_error_message='Invalid priority value'
            ),
            # Status constraint
            models.CheckConstraint(
                check=Q(status__in=['TODO', 'IN_PROGRESS', 'REVIEW', 'DONE', 'CANCELLED']),
                name='chk_task_status',
                violation_error_message='Invalid status value'
            ),
        ]
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for assignee queries
            models.Index(
                fields=['assignee_id'],
                name='idx_tasks_assignee'
            ),
            # Index for entity linking
            models.Index(
                fields=['entity_type', 'entity_id'],
                name='idx_tasks_entity'
            ),
            # Index for active tasks
            models.Index(
                fields=['status'],
                condition=Q(status__in=['TODO', 'IN_PROGRESS', 'REVIEW']),
                name='idx_tasks_status'
            ),
            # Index for overdue tasks
            models.Index(
                fields=['due_date', 'status'],
                name='idx_tasks_due_status'
            ),
            # Index for tenant queries
            models.Index(
                fields=['tenant', 'status'],
                name='idx_tasks_tenant_status'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.title} ({self.get_status_display()})"

    def clean(self):
        """Validate task"""
        if self.priority not in dict(self.PRIORITY_CHOICES):
            raise ValidationError('Invalid priority')
        
        if self.status not in dict(self.STATUS_CHOICES):
            raise ValidationError('Invalid status')

    def save(self, *args, **kwargs):
        """Override save to enforce business rules"""
        self.clean()
        
        # Set completed_at when marking done
        if self.status == 'DONE' and not self.completed_at:
            self.completed_at = timezone.now()
        
        # Clear completed_at if status changes from DONE
        if self.status != 'DONE' and self.completed_at:
            self.completed_at = None
        
        super().save(*args, **kwargs)

    # ========================================================================
    # STATUS TRANSITION METHODS
    # ========================================================================

    def move_to_in_progress(self):
        """
        Move task to in progress
        
        Example:
            task.move_to_in_progress()
        """
        if self.status == 'TODO':
            self.status = 'IN_PROGRESS'
            self.save()

    def move_to_review(self):
        """
        Move task to review
        
        Example:
            task.move_to_review()
        """
        if self.status in ['TODO', 'IN_PROGRESS']:
            self.status = 'REVIEW'
            self.save()

    def mark_done(self):
        """
        Mark task as done
        
        Example:
            task.mark_done()
        """
        if self.status != 'DONE':
            self.status = 'DONE'
            self.completed_at = timezone.now()
            self.save()

    def cancel(self):
        """
        Cancel task
        
        Example:
            task.cancel()
        """
        if self.status != 'DONE':
            self.status = 'CANCELLED'
            self.save()

    def reopen(self):
        """
        Reopen cancelled or done task
        
        Example:
            task.reopen()
        """
        if self.status in ['DONE', 'CANCELLED']:
            self.status = 'TODO'
            self.completed_at = None
            self.save()

    # ========================================================================
    # STATUS CHECK METHODS
    # ========================================================================

    def is_todo(self):
        """Check if task is to do"""
        return self.status == 'TODO'

    def is_in_progress(self):
        """Check if task is in progress"""
        return self.status == 'IN_PROGRESS'

    def is_in_review(self):
        """Check if task is in review"""
        return self.status == 'REVIEW'

    def is_done(self):
        """Check if task is done"""
        return self.status == 'DONE'

    def is_cancelled(self):
        """Check if task is cancelled"""
        return self.status == 'CANCELLED'

    def is_active(self):
        """Check if task is active"""
        return self.status in ['TODO', 'IN_PROGRESS', 'REVIEW']

    def is_overdue(self):
        """
        Check if task is overdue
        
        Returns:
            Boolean
        
        Example:
            if task.is_overdue():
                # Task is overdue
        """
        if not self.due_date or self.is_done():
            return False
        
        return timezone.now() > self.due_date

    def is_due_soon(self, hours=24):
        """
        Check if task is due soon
        
        Args:
            hours: Hours to check ahead
        
        Returns:
            Boolean
        
        Example:
            if task.is_due_soon(hours=24):
                # Task is due within 24 hours
        """
        if not self.due_date or self.is_done():
            return False
        
        now = timezone.now()
        due_soon = now + timedelta(hours=hours)
        
        return now < self.due_date <= due_soon

    # ========================================================================
    # DURATION METHODS
    # ========================================================================

    def get_duration(self):
        """
        Get task duration
        
        Returns:
            timedelta or None
        
        Example:
            duration = task.get_duration()
        """
        if self.completed_at:
            return self.completed_at - self.created_at
        
        if self.status != 'TODO':
            return timezone.now() - self.created_at
        
        return None

    def get_duration_seconds(self):
        """
        Get task duration in seconds
        
        Returns:
            Integer or None
        
        Example:
            seconds = task.get_duration_seconds()
        """
        duration = self.get_duration()
        if duration:
            return int(duration.total_seconds())
        return None

    def get_time_to_due(self):
        """
        Get time remaining until due
        
        Returns:
            timedelta or None
        
        Example:
            time_left = task.get_time_to_due()
        """
        if not self.due_date or self.is_done():
            return None
        
        return self.due_date - timezone.now()

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def get_user_tasks(cls, user, status=None, priority=None):
        """
        Get tasks assigned to user
        
        Args:
            user: UserAccount instance
            status: Optional status filter
            priority: Optional priority filter
        
        Returns:
            QuerySet of Task objects
        
        Example:
            tasks = Task.get_user_tasks(user, status='TODO')
        """
        query = cls.objects.filter(assignee=user)
        
        if status:
            query = query.filter(status=status)
        
        if priority:
            query = query.filter(priority=priority)
        
        return query

    @classmethod
    def get_active_tasks(cls, tenant=None):
        """
        Get all active tasks
        
        Args:
            tenant: Optional tenant filter
        
        Returns:
            QuerySet of Task objects
        
        Example:
            active = Task.get_active_tasks(tenant)
        """
        query = cls.objects.filter(
            status__in=['TODO', 'IN_PROGRESS', 'REVIEW']
        )
        
        if tenant:
            query = query.filter(tenant=tenant)
        
        return query

    @classmethod
    def get_overdue_tasks(cls, tenant=None):
        """
        Get all overdue tasks
        
        Args:
            tenant: Optional tenant filter
        
        Returns:
            QuerySet of Task objects
        
        Example:
            overdue = Task.get_overdue_tasks(tenant)
        """
        now = timezone.now()
        
        query = cls.objects.filter(
            due_date__lt=now,
            status__in=['TODO', 'IN_PROGRESS', 'REVIEW']
        )
        
        if tenant:
            query = query.filter(tenant=tenant)
        
        return query

    @classmethod
    def get_due_soon_tasks(cls, hours=24, tenant=None):
        """
        Get tasks due soon
        
        Args:
            hours: Hours to check ahead
            tenant: Optional tenant filter
        
        Returns:
            QuerySet of Task objects
        
        Example:
            due_soon = Task.get_due_soon_tasks(hours=24)
        """
        now = timezone.now()
        due_soon = now + timedelta(hours=hours)
        
        query = cls.objects.filter(
            due_date__range=[now, due_soon],
            status__in=['TODO', 'IN_PROGRESS', 'REVIEW']
        )
        
        if tenant:
            query = query.filter(tenant=tenant)
        
        return query

    @classmethod
    def get_entity_tasks(cls, entity_type, entity_id, status=None):
        """
        Get tasks linked to entity
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
            status: Optional status filter
        
        Returns:
            QuerySet of Task objects
        
        Example:
            tasks = Task.get_entity_tasks('vehicles', vehicle.id)
        """
        query = cls.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id
        )
        
        if status:
            query = query.filter(status=status)
        
        return query

    # ========================================================================
    # BULK OPERATION METHODS
    # ========================================================================

    @classmethod
    def bulk_update_status(cls, task_ids, new_status):
        """
        Bulk update task status
        
        Args:
            task_ids: List of task IDs
            new_status: New status
        
        Returns:
            Number of updated tasks
        
        Example:
            count = Task.bulk_update_status([1, 2, 3], 'DONE')
        """
        if new_status == 'DONE':
            return cls.objects.filter(id__in=task_ids).update(
                status=new_status,
                completed_at=timezone.now()
            )
        
        return cls.objects.filter(id__in=task_ids).update(
            status=new_status
        )

    @classmethod
    def bulk_assign(cls, task_ids, assignee):
        """
        Bulk assign tasks
        
        Args:
            task_ids: List of task IDs
            assignee: UserAccount instance
        
        Returns:
            Number of updated tasks
        
        Example:
            count = Task.bulk_assign([1, 2, 3], user)
        """
        return cls.objects.filter(id__in=task_ids).update(
            assignee=assignee
        )

    @classmethod
    def bulk_set_priority(cls, task_ids, priority):
        """
        Bulk set task priority
        
        Args:
            task_ids: List of task IDs
            priority: Priority level
        
        Returns:
            Number of updated tasks
        
        Example:
            count = Task.bulk_set_priority([1, 2, 3], 'HIGH')
        """
        return cls.objects.filter(id__in=task_ids).update(
            priority=priority
        )

    @classmethod
    def bulk_set_due_date(cls, task_ids, due_date):
        """
        Bulk set task due date
        
        Args:
            task_ids: List of task IDs
            due_date: Due date
        
        Returns:
            Number of updated tasks
        
        Example:
            count = Task.bulk_set_due_date([1, 2, 3], due_date)
        """
        return cls.objects.filter(id__in=task_ids).update(
            due_date=due_date
        )

    # ========================================================================
    # STATISTICS METHODS
    # ========================================================================

    @classmethod
    def get_statistics(cls, tenant=None):
        """
        Get task statistics
        
        Args:
            tenant: Optional tenant filter
        
        Returns:
            Dictionary with statistics
        
        Example:
            stats = Task.get_statistics(tenant)
        """
        query = cls.objects.all()
        
        if tenant:
            query = query.filter(tenant=tenant)
        
        total = query.count()
        
        if total == 0:
            return {
                'total': 0,
                'todo': 0,
                'in_progress': 0,
                'review': 0,
                'done': 0,
                'cancelled': 0,
                'overdue': 0,
                'completion_rate': 0
            }
        
        todo = query.filter(status='TODO').count()
        in_progress = query.filter(status='IN_PROGRESS').count()
        review = query.filter(status='REVIEW').count()
        done = query.filter(status='DONE').count()
        cancelled = query.filter(status='CANCELLED').count()
        overdue = cls.get_overdue_tasks(tenant).count()
        
        completion_rate = (done / (total - cancelled) * 100) if (total - cancelled) > 0 else 0
        
        return {
            'total': total,
            'todo': todo,
            'in_progress': in_progress,
            'review': review,
            'done': done,
            'cancelled': cancelled,
            'overdue': overdue,
            'completion_rate': completion_rate
        }

    @classmethod
    def get_user_statistics(cls, user):
        """
        Get user task statistics
        
        Args:
            user: UserAccount instance
        
        Returns:
            Dictionary with statistics
        
        Example:
            stats = Task.get_user_statistics(user)
        """
        tasks = cls.objects.filter(assignee=user)
        
        total = tasks.count()
        
        if total == 0:
            return {
                'total': 0,
                'todo': 0,
                'in_progress': 0,
                'review': 0,
                'done': 0,
                'overdue': 0
            }
        
        todo = tasks.filter(status='TODO').count()
        in_progress = tasks.filter(status='IN_PROGRESS').count()
        review = tasks.filter(status='REVIEW').count()
        done = tasks.filter(status='DONE').count()
        
        now = timezone.now()
        overdue = tasks.filter(
            due_date__lt=now,
            status__in=['TODO', 'IN_PROGRESS', 'REVIEW']
        ).count()
        
        return {
            'total': total,
            'todo': todo,
            'in_progress': in_progress,
            'review': review,
            'done': done,
            'overdue': overdue
        }

    @classmethod
    def get_priority_distribution(cls, tenant=None):
        """
        Get task distribution by priority
        
        Args:
            tenant: Optional tenant filter
        
        Returns:
            Dictionary with priority counts
        
        Example:
            dist = Task.get_priority_distribution(tenant)
        """
        query = cls.objects.all()
        
        if tenant:
            query = query.filter(tenant=tenant)
        
        return {
            'LOW': query.filter(priority='LOW').count(),
            'MEDIUM': query.filter(priority='MEDIUM').count(),
            'HIGH': query.filter(priority='HIGH').count(),
            'URGENT': query.filter(priority='URGENT').count(),
        }