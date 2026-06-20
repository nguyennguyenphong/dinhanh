from dataclasses import dataclass


@dataclass(frozen=True)
class SessionEntity:
    deleted: str
    deleted_by_cascade: bool
    created_at: str
    updated_at: str
    id: int
    session_token: str
    refresh_token: str
    device_info: str
    ip_address: str
    user_agent: str
    expires_at: str
    last_activity: str
    revoked_at: str
    revocation_reason: str
    created_by_id: int
    updated_by_id: int
    user_id: int

    # Business rules

    def is_revoked(self):
        return self.revoked_at

    def is_active(self):
        return not self.is_revoked()

    def is_expired(self):
        return self.expires_at

    def is_valid(self):
        return self.is_active() and not self.is_expired()

    def is_invalid(self):
        return not self.is_valid()

    def is_deleted(self):
        return self.deleted

    def is_deleted_by_cascade(self):
        return self.deleted_by_cascade

    def is_created(self):
        return self.created_at

    def is_updated(self):
        return self.updated_at

    def is_deleted(self):
        return self.deleted

    def is_deleted_by_cascade(self):
        return self.deleted_by_cascade
