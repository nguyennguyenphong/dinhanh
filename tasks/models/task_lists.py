# ============================================================================
# FILE: apps/tasks/models.py
# Task List and Task Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from tenants.models.tenants import Tenant
from tasks.models.tasks import Task

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
