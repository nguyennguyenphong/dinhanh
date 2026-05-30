# ============================================================================
# FILE: apps/tasks/models.py
# Task List and Task Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from tenants.models.tenants import Tenant


class TaskList(models.Model):
    """
    Task list model for organizing tasks
    
    Features:
    - Multi-tenant support: Each tenant has own task lists
    - Branch assignment: Assign to specific branches
    - Creator tracking: Track who created the list
    - Task organization: Group related tasks
    - Audit trail: Track creation and updates
    - Statistics: Track task counts and status
    
    Use Cases:
    - Daily maintenance checklists
    - Vehicle inspection lists
    - Employee onboarding tasks
    - Trip preparation lists
    - Safety compliance tasks
    - Quality assurance checklists
    
    Example:
        # Create task list
        task_list = TaskList.objects.create(
            tenant=tenant,
            name='Daily Vehicle Inspection',
            branch=branch,
            created_by=user
        )
        
        # Add tasks
        task_list.add_task(
            title='Check tire pressure',
            description='Verify tire pressure is correct',
            priority='high'
        )
        
        # Get statistics
        stats = task_list.get_statistics()
    """

    id = models.AutoField(primary_key=True)
    
    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='task_lists',
        db_index=True,
        help_text='Tenant that owns this task list'
    )
    
    # ========================================================================
    # TASK LIST INFORMATION
    # ========================================================================
    
    name = models.CharField(
        max_length=100,
        help_text='Name of the task list'
    )
    
    # ========================================================================
    # ORGANIZATION
    # ========================================================================
    
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='task_lists',
        help_text='Branch this task list belongs to'
    )
    
    # ========================================================================
    # AUDIT INFORMATION
    # ========================================================================
    
    created_by = models.ForeignKey(
        'accounts.UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='task_lists_created',
        help_text='User who created this task list'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When this task list was created'
    )

    class Meta:
        db_table = 'task_lists'
        verbose_name = _('Task List')
        verbose_name_plural = _('Task Lists')
        ordering = ['-created_at']
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for finding task lists by tenant
            models.Index(
                fields=['tenant'],
                name='idx_task_list_tenant'
            ),
            # Index for finding task lists by branch
            models.Index(
                fields=['branch'],
                name='idx_task_list_branch'
            ),
            # Index for finding task lists by creator
            models.Index(
                fields=['created_by'],
                name='idx_task_list_creator'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.name} ({self.tenant.code})"

    # ========================================================================
    # TASK MANAGEMENT
    # ========================================================================

    def add_task(self, title, description='', priority='normal', 
                 due_date=None, assigned_to=None):
        """
        Add task to list
        
        Args:
            title: Task title
            description: Task description
            priority: Task priority (low, normal, high, urgent)
            due_date: Due date for task
            assigned_to: UserAccount to assign task to
        
        Returns:
            Task instance
        
        Example:
            task = task_list.add_task(
                title='Check tire pressure',
                description='Verify tire pressure is correct',
                priority='high',
                assigned_to=user
            )
        """
        task = Task.objects.create(
            task_list=self,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            assigned_to=assigned_to
        )
        return task

    def get_tasks(self, status=None, assigned_to=None):
        """
        Get tasks in this list
        
        Args:
            status: Optional status filter
            assigned_to: Optional user filter
        
        Returns:
            QuerySet of Task objects
        
        Example:
            tasks = task_list.get_tasks(status='pending')
        """
        query = self.tasks.all()
        
        if status:
            query = query.filter(status=status)
        
        if assigned_to:
            query = query.filter(assigned_to=assigned_to)
        
        return query.order_by('-priority', 'due_date')

    def get_statistics(self):
        """
        Get task list statistics
        
        Returns:
            Dictionary with statistics
        
        Example:
            stats = task_list.get_statistics()
            # Returns: {
            #     'total': 10,
            #     'pending': 5,
            #     'in_progress': 3,
            #     'completed': 2,
            #     'completion_rate': 20.0
            # }
        """
        tasks = self.tasks.all()
        total = tasks.count()
        
        if total == 0:
            return {
                'total': 0,
                'pending': 0,
                'in_progress': 0,
                'completed': 0,
                'completion_rate': 0
            }
        
        pending = tasks.filter(status='pending').count()
        in_progress = tasks.filter(status='in_progress').count()
        completed = tasks.filter(status='completed').count()
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'completed': completed,
            'completion_rate': completion_rate
        }

    def get_overdue_tasks(self):
        """
        Get overdue tasks
        
        Returns:
            QuerySet of Task objects
        
        Example:
            overdue = task_list.get_overdue_tasks()
        """
        return self.tasks.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        )

    def mark_all_completed(self):
        """
        Mark all tasks as completed
        
        Returns:
            Number of updated tasks
        
        Example:
            count = task_list.mark_all_completed()
        """
        count = self.tasks.exclude(status='completed').update(
            status='completed',
            completed_at=timezone.now()
        )
        return count


class Task(models.Model):
    """
    Task model for individual tasks
    
    Features:
    - Task assignment: Assign to users
    - Priority levels: low, normal, high, urgent
    - Status tracking: Track task progress
    - Due dates: Set deadlines
    - Completion tracking: Track completion time
    - Comments: Add task comments
    - Attachments: Attach files to tasks
    - Audit trail: Track changes
    
    Status Flow:
    pending -> in_progress -> completed
    pending -> cancelled
    in_progress -> cancelled
    
    Example:
        # Create task
        task = Task.objects.create(
            task_list=task_list,
            title='Check tire pressure',
            priority='high',
            assigned_to=user
        )
        
        # Update status
        task.start()
        task.complete()
        
        # Add comment
        task.add_comment(user, 'Tire pressure is correct')
    """

    PRIORITY_CHOICES = (
        ('low', _('Low - Can be done anytime')),
        ('normal', _('Normal - Regular priority')),
        ('high', _('High - Important task')),
        ('urgent', _('Urgent - Must be done immediately')),
    )

    STATUS_CHOICES = (
        ('pending', _('Pending - Not started')),
        ('in_progress', _('In Progress - Currently being worked on')),
        ('completed', _('Completed - Task finished')),
        ('cancelled', _('Cancelled - Task cancelled')),
    )

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    task_list = models.ForeignKey(
        TaskList,
        on_delete=models.CASCADE,
        related_name='tasks',
        db_index=True,
        help_text='Task list this task belongs to'
    )
    
    # ========================================================================
    # TASK INFORMATION
    # ========================================================================
    
    title = models.CharField(
        max_length=200,
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
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal',
        db_index=True,
        help_text='Task priority'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text='Task status'
    )
    
    # ========================================================================
    # ASSIGNMENT
    # ========================================================================
    
    assigned_to = models.ForeignKey(
        'accounts.UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        help_text='User this task is assigned to'
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
    
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When task was started'
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When task was completed'
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
        ordering = ['-priority', 'due_date']
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for finding tasks by status
            models.Index(
                fields=['status'],
                name='idx_task_status'
            ),
            # Index for finding tasks by assignee
            models.Index(
                fields=['assigned_to'],
                name='idx_task_assigned_to'
            ),
            # Index for finding overdue tasks
            models.Index(
                fields=['due_date', 'status'],
                name='idx_task_due_status'
            ),
            # Index for finding tasks by priority
            models.Index(
                fields=['priority'],
                name='idx_task_priority'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.title} ({self.get_status_display()})"

    # ========================================================================
    # STATUS METHODS
    # ========================================================================

    def start(self):
        """
        Start task
        
        Example:
            task.start()
        """
        if self.status == 'pending':
            self.status = 'in_progress'
            self.started_at = timezone.now()
            self.save()

    def complete(self):
        """
        Complete task
        
        Example:
            task.complete()
        """
        if self.status in ['pending', 'in_progress']:
            self.status = 'completed'
            self.completed_at = timezone.now()
            if not self.started_at:
                self.started_at = timezone.now()
            self.save()

    def cancel(self):
        """
        Cancel task
        
        Example:
            task.cancel()
        """
        if self.status != 'completed':
            self.status = 'cancelled'
            self.save()

    def is_overdue(self):
        """
        Check if task is overdue
        
        Returns:
            Boolean
        
        Example:
            if task.is_overdue():
                # Task is overdue
        """
        if not self.due_date:
            return False
        
        if self.status == 'completed':
            return False
        
        return timezone.now() > self.due_date

    def get_duration(self):
        """
        Get task duration
        
        Returns:
            timedelta or None
        
        Example:
            duration = task.get_duration()
        """
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        
        if self.started_at:
            return timezone.now() - self.started_at
        
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

    # ========================================================================
    # COMMENT METHODS
    # ========================================================================

    def add_comment(self, user, text):
        """
        Add comment to task
        
        Args:
            user: UserAccount instance
            text: Comment text
        
        Returns:
            TaskComment instance
        
        Example:
            comment = task.add_comment(user, 'Tire pressure is correct')
        """
        return TaskComment.objects.create(
            task=self,
            user=user,
            text=text
        )

    def get_comments(self):
        """
        Get task comments
        
        Returns:
            QuerySet of TaskComment objects
        
        Example:
            comments = task.get_comments()
        """
        return self.comments.all().order_by('-created_at')

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def get_user_tasks(cls, user, status=None):
        """
        Get tasks assigned to user
        
        Args:
            user: UserAccount instance
            status: Optional status filter
        
        Returns:
            QuerySet of Task objects
        
        Example:
            tasks = Task.get_user_tasks(user, status='pending')
        """
        query = cls.objects.filter(assigned_to=user)
        
        if status:
            query = query.filter(status=status)
        
        return query.order_by('-priority', 'due_date')

    @classmethod
    def get_overdue_tasks(cls):
        """
        Get all overdue tasks
        
        Returns:
            QuerySet of Task objects
        
        Example:
            overdue = Task.get_overdue_tasks()
        """
        return cls.objects.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        )

    @classmethod
    def get_pending_tasks(cls):
        """
        Get all pending tasks
        
        Returns:
            QuerySet of Task objects
        
        Example:
            pending = Task.get_pending_tasks()
        """
        return cls.objects.filter(status='pending')

    @classmethod
    def get_statistics(cls):
        """
        Get task statistics
        
        Returns:
            Dictionary with statistics
        
        Example:
            stats = Task.get_statistics()
        """
        total = cls.objects.count()
        pending = cls.objects.filter(status='pending').count()
        in_progress = cls.objects.filter(status='in_progress').count()
        completed = cls.objects.filter(status='completed').count()
        cancelled = cls.objects.filter(status='cancelled').count()
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'completed': completed,
            'cancelled': cancelled,
            'completion_rate': completion_rate
        }


class TaskComment(models.Model):
    """
    Task comment model for task discussions
    
    Features:
    - User comments: Add comments to tasks
    - Timestamps: Track when comments were added
    - Audit trail: Track who commented
    
    Example:
        # Add comment
        comment = TaskComment.objects.create(
            task=task,
            user=user,
            text='Tire pressure is correct'
        )
    """

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        db_index=True,
        help_text='Task this comment belongs to'
    )
    
    user = models.ForeignKey(
        'accounts.UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='task_comments',
        help_text='User who made this comment'
    )
    
    # ========================================================================
    # COMMENT CONTENT
    # ========================================================================
    
    text = models.TextField(
        help_text='Comment text'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When comment was created'
    )

    class Meta:
        db_table = 'task_comments'
        verbose_name = _('Task Comment')
        verbose_name_plural = _('Task Comments')
        ordering = ['-created_at']
        
        indexes = [
            models.Index(
                fields=['task'],
                name='idx_task_comment_task'
            ),
            models.Index(
                fields=['user'],
                name='idx_task_comment_user'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"Comment on {self.task.title}"