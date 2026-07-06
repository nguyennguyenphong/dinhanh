# Import models from module in this package
# This is to avoid circular imports
# Example:
# from branches.models.branches import Branch

from branches.models.branch_audit_log import BranchAuditLog
from branches.models.branches import Branch

__all__ = [
    "Branch",
    "BranchAuditLog",
]
