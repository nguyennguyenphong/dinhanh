# Import models from module in this package
# This is to avoid circular imports
# Example:
# from comments.models.comments import Comment

from comments.models.comments import Comment

__all__ = [
    "Comment",
]
