-- =============================================================================
-- DINH ANH BUS CMS - PostgreSQL Enterprise Schema v2.0
-- Production-grade | Multi-branch | Scalable | Future-proof
-- Generated: 2025-05-29
-- =============================================================================
-- Changelog từ v1.1:
--   + APP: menus          (dynamic sidebar/nav driven by DB)
--   + APP: system_config  (key-value configs per env/branch)
--   + APP: feature_flags  (feature toggle per user/role/branch)
--   + APP: tenants        (multi-tenant ready)
--   + APP: api_tokens     (3rd party & internal API key mgmt)
--   + APP: media          (central file/media management)
--   + APP: tags           (generic tagging system)
--   + APP: comments       (generic comment/note system)
--   + APP: tasks          (internal task/todo tracking)
--   + APP: webhooks       (outbound event hooks)
--   + Thêm triggers tự động cập nhật updated_at
--   + Thêm CHECK constraints chuẩn hóa enum values
--   + Bổ sung indexes GIN cho JSONB và trgm cho full-text search
--   + Bổ sung partitioning strategy cho bảng lớn (audit_logs, notifications)
-- =============================================================================

-- ---------------------------------------------------------------------------
-- EXTENSIONS
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";    -- gen_random_bytes cho API keys

-- ---------------------------------------------------------------------------
-- HELPER: auto-update updated_at
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Macro để gắn trigger nhanh (gọi sau mỗi CREATE TABLE có updated_at)
-- Usage: SELECT create_updated_at_trigger('table_name');
CREATE OR REPLACE FUNCTION create_updated_at_trigger(tbl TEXT)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    EXECUTE format(
        'CREATE TRIGGER trg_%s_updated_at
         BEFORE UPDATE ON %I
         FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at()',
        tbl, tbl
    );
END;
$$;

-- =============================================================================
-- APP: tenants  (multi-tenant foundation — 1 tenant = 1 nhà xe)
-- Khi chạy single-tenant, tất cả records thuộc tenant_id = 1
-- =============================================================================

CREATE TABLE tenants (
    id            SERIAL PRIMARY KEY,
    uuid          UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    code          VARCHAR(30)  NOT NULL UNIQUE,      -- e.g. "DINHANH"
    name          VARCHAR(255) NOT NULL,
    domain        VARCHAR(255),                       -- custom domain nếu SaaS
    logo_url      VARCHAR(500),
    primary_color VARCHAR(7)   NOT NULL DEFAULT '#3B82F6',
    plan          VARCHAR(30)  NOT NULL DEFAULT 'STANDARD',
    -- TRIAL, STANDARD, PROFESSIONAL, ENTERPRISE
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    settings      JSONB        NOT NULL DEFAULT '{}', -- tenant-level overrides
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_tenant_plan CHECK (plan IN ('TRIAL','STANDARD','PROFESSIONAL','ENTERPRISE'))
);
SELECT create_updated_at_trigger('tenants');

-- Default tenant
INSERT INTO tenants (code, name, plan) VALUES ('DINHANH', 'Nhà Xe Đinh Anh', 'PROFESSIONAL');

-- =============================================================================
-- APP: accounts
-- =============================================================================

CREATE TABLE roles (
    id          SERIAL PRIMARY KEY,
    tenant_id   INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    name        VARCHAR(100) NOT NULL,
    slug        VARCHAR(100) NOT NULL,               -- e.g. "super-admin", "cashier"
    description TEXT,
    is_system   BOOLEAN      NOT NULL DEFAULT FALSE, -- system roles không xóa được
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, slug)
);
SELECT create_updated_at_trigger('roles');

CREATE TABLE permissions (
    id          SERIAL PRIMARY KEY,
    codename    VARCHAR(150) NOT NULL UNIQUE,         -- e.g. "tickets.add_ticket"
    name        VARCHAR(255) NOT NULL,
    module      VARCHAR(100) NOT NULL,                -- e.g. "tickets", "vehicles"
    action      VARCHAR(30)  NOT NULL DEFAULT 'view', -- view, add, change, delete, export
    description TEXT,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_permission_action CHECK (action IN ('view','add','change','delete','export','approve','all'))
);

CREATE TABLE role_permissions (
    role_id       INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE user_accounts (
    id            SERIAL PRIMARY KEY,
    uuid          UUID         NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    tenant_id     INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    username      VARCHAR(150) NOT NULL,
    email         VARCHAR(254) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(255) NOT NULL,
    phone         VARCHAR(20),
    avatar        VARCHAR(500),
    branch_id     INTEGER,                            -- FK added after branches
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    is_staff      BOOLEAN      NOT NULL DEFAULT FALSE,
    is_superuser  BOOLEAN      NOT NULL DEFAULT FALSE,
    must_change_pw BOOLEAN     NOT NULL DEFAULT FALSE,
    two_fa_enabled BOOLEAN     NOT NULL DEFAULT FALSE,
    two_fa_secret  VARCHAR(100),
    last_login    TIMESTAMPTZ,
    last_login_ip INET,
    failed_login_count SMALLINT NOT NULL DEFAULT 0,
    locked_until  TIMESTAMPTZ,
    preferences   JSONB        NOT NULL DEFAULT '{}', -- per-user UI preferences
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, username),
    UNIQUE (tenant_id, email)
);
SELECT create_updated_at_trigger('user_accounts');

CREATE TABLE user_roles (
    user_id    INTEGER NOT NULL REFERENCES user_accounts(id) ON DELETE CASCADE,
    role_id    INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    granted_by INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, role_id)
);

-- Session / refresh token management
CREATE TABLE user_sessions (
    id            BIGSERIAL PRIMARY KEY,
    user_id       INTEGER      NOT NULL REFERENCES user_accounts(id) ON DELETE CASCADE,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    refresh_token VARCHAR(255) UNIQUE,
    device_info   TEXT,
    ip_address    INET,
    user_agent    TEXT,
    expires_at    TIMESTAMPTZ  NOT NULL,
    revoked_at    TIMESTAMPTZ,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_sessions_token   ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_user    ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires ON user_sessions(expires_at);

CREATE TABLE audit_logs (
    id          BIGSERIAL   PRIMARY KEY,
    tenant_id   INTEGER     NOT NULL DEFAULT 1,
    user_id     INTEGER     REFERENCES user_accounts(id) ON DELETE SET NULL,
    username    VARCHAR(150),
    action      VARCHAR(50) NOT NULL,
    module      VARCHAR(100) NOT NULL,
    object_id   VARCHAR(50),
    object_repr VARCHAR(500),
    changes     JSONB,
    ip_address  INET,
    user_agent  TEXT,
    request_id  UUID,                                 -- correlation ID per request
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Partitions theo năm (tạo thêm hàng năm)
CREATE TABLE audit_logs_2025 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE audit_logs_2026 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
CREATE TABLE audit_logs_2027 PARTITION OF audit_logs
    FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');

CREATE INDEX idx_audit_user    ON audit_logs(user_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_module  ON audit_logs(module, action);
CREATE INDEX idx_audit_object  ON audit_logs(object_id) WHERE object_id IS NOT NULL;

-- =============================================================================
-- APP: branches
-- =============================================================================

CREATE TABLE branches (
    id          SERIAL PRIMARY KEY,
    tenant_id   INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    code        VARCHAR(20)  NOT NULL,
    name        VARCHAR(255) NOT NULL,
    address     TEXT,
    phone       VARCHAR(20),
    email       VARCHAR(254),
    manager_id  INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    timezone    VARCHAR(50)  NOT NULL DEFAULT 'Asia/Ho_Chi_Minh',
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    metadata    JSONB        NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, code)
);
SELECT create_updated_at_trigger('branches');

ALTER TABLE user_accounts
    ADD CONSTRAINT fk_user_branch FOREIGN KEY (branch_id)
    REFERENCES branches(id) ON DELETE SET NULL;

-- =============================================================================
-- APP: menus  (Dynamic navigation — driven by DB, mapped to permissions)
-- =============================================================================

CREATE TABLE menu_groups (
    id          SERIAL PRIMARY KEY,
    tenant_id   INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    code        VARCHAR(50)  NOT NULL,
    label       VARCHAR(100) NOT NULL,               -- e.g. "Vận hành xe"
    icon        TEXT,                                 -- SVG path string hoặc icon name
    sort_order  SMALLINT     NOT NULL DEFAULT 0,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, code)
);
SELECT create_updated_at_trigger('menu_groups');

CREATE TABLE menu_items (
    id              SERIAL PRIMARY KEY,
    tenant_id       INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    group_id        INTEGER      REFERENCES menu_groups(id) ON DELETE SET NULL,
    parent_id       INTEGER      REFERENCES menu_items(id) ON DELETE CASCADE,  -- nested menus
    code            VARCHAR(80)  NOT NULL,
    label           VARCHAR(150) NOT NULL,
    url_name        VARCHAR(150),                     -- Django url_name or route name
    url_path        VARCHAR(300),                     -- static path fallback
    icon            TEXT,
    badge_text      VARCHAR(30),                      -- "NEW", "BETA", số thông báo
    badge_color     VARCHAR(7)   DEFAULT '#EF4444',
    permission_code VARCHAR(150) REFERENCES permissions(codename) ON DELETE SET NULL,
    sort_order      SMALLINT     NOT NULL DEFAULT 0,
    open_in_new_tab BOOLEAN      NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    is_hidden       BOOLEAN      NOT NULL DEFAULT FALSE, -- ẩn nhưng route vẫn hoạt động
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, code)
);
SELECT create_updated_at_trigger('menu_items');

-- Hiển thị menu theo role (nếu NULL = tất cả role có permission đều thấy)
CREATE TABLE menu_item_roles (
    menu_item_id INTEGER NOT NULL REFERENCES menu_items(id) ON DELETE CASCADE,
    role_id      INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (menu_item_id, role_id)
);

CREATE INDEX idx_menu_items_group  ON menu_items(group_id);
CREATE INDEX idx_menu_items_parent ON menu_items(parent_id);
CREATE INDEX idx_menu_items_sort   ON menu_items(group_id, sort_order);

-- =============================================================================
-- APP: system_config  (Key-value configuration store)
-- =============================================================================

CREATE TABLE system_configs (
    id           SERIAL PRIMARY KEY,
    tenant_id    INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    category     VARCHAR(60)  NOT NULL,   -- GENERAL, PAYMENT, SMS, EMAIL, BOOKING, PRINTING, ...
    key          VARCHAR(120) NOT NULL,
    value        TEXT,
    value_type   VARCHAR(20)  NOT NULL DEFAULT 'string',
    -- string, integer, boolean, json, secret
    label        VARCHAR(255) NOT NULL,
    description  TEXT,
    is_encrypted BOOLEAN      NOT NULL DEFAULT FALSE,
    is_public    BOOLEAN      NOT NULL DEFAULT FALSE, -- exposed to frontend?
    is_readonly  BOOLEAN      NOT NULL DEFAULT FALSE, -- locked in production
    env          VARCHAR(20)  NOT NULL DEFAULT 'ALL',
    -- ALL, DEVELOPMENT, STAGING, PRODUCTION
    updated_by   INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, category, key),
    CONSTRAINT chk_config_type  CHECK (value_type IN ('string','integer','boolean','json','secret','text')),
    CONSTRAINT chk_config_env   CHECK (env IN ('ALL','DEVELOPMENT','STAGING','PRODUCTION'))
);
SELECT create_updated_at_trigger('system_configs');

-- Config change history
CREATE TABLE system_config_history (
    id           BIGSERIAL PRIMARY KEY,
    config_id    INTEGER      NOT NULL REFERENCES system_configs(id) ON DELETE CASCADE,
    old_value    TEXT,
    new_value    TEXT,
    changed_by   INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    changed_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Seed cấu hình cơ bản
INSERT INTO system_configs (category, key, value, value_type, label, is_public) VALUES
('GENERAL',  'company_name',          'Nhà Xe Đinh Anh',   'string',  'Tên công ty',              TRUE),
('GENERAL',  'company_phone',         '0800 123 456',       'string',  'Hotline',                  TRUE),
('GENERAL',  'company_address',       '',                   'string',  'Địa chỉ trụ sở',           TRUE),
('GENERAL',  'default_timezone',      'Asia/Ho_Chi_Minh',   'string',  'Múi giờ mặc định',         FALSE),
('GENERAL',  'default_currency',      'VND',                'string',  'Đơn vị tiền tệ',           TRUE),
('BOOKING',  'max_seats_per_booking', '10',                 'integer', 'Số ghế tối đa/1 lần đặt',  FALSE),
('BOOKING',  'booking_expire_min',    '15',                 'integer', 'Timeout giữ ghế (phút)',    FALSE),
('BOOKING',  'allow_online_booking',  'true',               'boolean', 'Cho phép đặt vé online',   FALSE),
('PAYMENT',  'vat_rate',              '10',                 'integer', 'Thuế VAT (%)',              FALSE),
('PAYMENT',  'allow_cod',             'true',               'boolean', 'Cho phép thanh toán COD',   FALSE),
('PRINTING', 'ticket_template',       'default',            'string',  'Mẫu in vé mặc định',       FALSE),
('PRINTING', 'printer_type',          'thermal_80mm',       'string',  'Loại máy in',              FALSE),
('SMS',      'provider',              'esms',               'string',  'Nhà cung cấp SMS',         FALSE),
('SMS',      'sender_name',           'DINHANH',            'string',  'Tên hiển thị SMS',         FALSE),
('EMAIL',    'from_name',             'Nhà Xe Đinh Anh',   'string',  'Tên gửi email',            FALSE),
('EMAIL',    'from_address',          'no-reply@dinhanh.vn','string',  'Email gửi đi',             FALSE);

-- =============================================================================
-- APP: feature_flags  (Toggle tính năng theo tenant/role/user)
-- =============================================================================

CREATE TABLE feature_flags (
    id           SERIAL PRIMARY KEY,
    tenant_id    INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    key          VARCHAR(100) NOT NULL,               -- e.g. "online_payment_vnpay"
    label        VARCHAR(255) NOT NULL,
    description  TEXT,
    is_enabled   BOOLEAN      NOT NULL DEFAULT FALSE,
    rollout_pct  SMALLINT     NOT NULL DEFAULT 100,   -- % users được bật (A/B testing)
    allowed_roles INTEGER[],                           -- NULL = tất cả roles
    allowed_users INTEGER[],                           -- whitelist user IDs
    valid_from   TIMESTAMPTZ,
    valid_to     TIMESTAMPTZ,
    metadata     JSONB        NOT NULL DEFAULT '{}',
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, key),
    CONSTRAINT chk_rollout_pct CHECK (rollout_pct BETWEEN 0 AND 100)
);
SELECT create_updated_at_trigger('feature_flags');

INSERT INTO feature_flags (key, label, is_enabled) VALUES
('online_booking',       'Đặt vé online',              TRUE),
('vnpay_payment',        'Thanh toán VNPay',            FALSE),
('momo_payment',         'Thanh toán MoMo',             FALSE),
('zalo_notification',    'Thông báo qua Zalo OA',       FALSE),
('loyalty_points',       'Điểm tích lũy khách hàng',   FALSE),
('dynamic_pricing',      'Giá vé động theo thời điểm', FALSE),
('qr_ticket',            'Vé QR Code',                  TRUE),
('e_invoice_auto',       'Xuất hoá đơn điện tử tự động',FALSE),
('driver_app',           'App tài xế',                  FALSE),
('customer_portal',      'Cổng thông tin khách hàng',  FALSE);

-- =============================================================================
-- APP: api_tokens  (Quản lý API keys: internal services, 3rd party, agents)
-- =============================================================================

CREATE TABLE api_tokens (
    id           SERIAL PRIMARY KEY,
    tenant_id    INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    name         VARCHAR(100) NOT NULL,               -- e.g. "Vé xe app mobile"
    token_hash   VARCHAR(255) NOT NULL UNIQUE,        -- sha256(token), không lưu raw
    token_prefix VARCHAR(8)   NOT NULL,               -- 8 ký tự đầu để nhận diện
    scopes       TEXT[]       NOT NULL DEFAULT '{}',  -- e.g. '{bookings.read,trips.read}'
    created_by   INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    branch_id    INTEGER      REFERENCES branches(id) ON DELETE SET NULL,
    last_used_at TIMESTAMPTZ,
    last_used_ip INET,
    expires_at   TIMESTAMPTZ,
    is_active    BOOLEAN      NOT NULL DEFAULT TRUE,
    request_count BIGINT      NOT NULL DEFAULT 0,
    rate_limit   INTEGER      NOT NULL DEFAULT 1000,  -- requests/hour
    notes        TEXT,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
SELECT create_updated_at_trigger('api_tokens');

CREATE INDEX idx_api_tokens_prefix ON api_tokens(token_prefix);
CREATE INDEX idx_api_tokens_active ON api_tokens(is_active) WHERE is_active = TRUE;

-- =============================================================================
-- APP: media  (Trung tâm quản lý file upload)
-- =============================================================================

CREATE TABLE media_files (
    id           BIGSERIAL PRIMARY KEY,
    tenant_id    INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    uuid         UUID         NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    original_name VARCHAR(500) NOT NULL,
    stored_name  VARCHAR(500) NOT NULL,
    storage      VARCHAR(30)  NOT NULL DEFAULT 'local',
    -- local, s3, gcs, azure
    bucket       VARCHAR(100),
    file_path    VARCHAR(1000) NOT NULL,
    url          VARCHAR(1000),
    mime_type    VARCHAR(100),
    size_bytes   BIGINT,
    width        INTEGER,
    height       INTEGER,
    is_public    BOOLEAN      NOT NULL DEFAULT FALSE,
    uploaded_by  INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    entity_type  VARCHAR(60),                          -- vehicles, employees, ...
    entity_id    INTEGER,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_media_entity ON media_files(entity_type, entity_id);
CREATE INDEX idx_media_uploader ON media_files(uploaded_by);

-- =============================================================================
-- APP: tags  (Generic tagging — gắn tag cho bất kỳ entity nào)
-- =============================================================================

CREATE TABLE tags (
    id         SERIAL PRIMARY KEY,
    tenant_id  INTEGER     NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    slug       VARCHAR(80) NOT NULL,
    label      VARCHAR(100) NOT NULL,
    color      VARCHAR(7)  NOT NULL DEFAULT '#6B7280',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, slug)
);

CREATE TABLE entity_tags (
    tag_id      INTEGER     NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    entity_type VARCHAR(60) NOT NULL,
    entity_id   BIGINT      NOT NULL,
    tagged_by   INTEGER     REFERENCES user_accounts(id) ON DELETE SET NULL,
    tagged_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (tag_id, entity_type, entity_id)
);

CREATE INDEX idx_entity_tags_lookup ON entity_tags(entity_type, entity_id);

-- =============================================================================
-- APP: webhooks  (Outbound event notifications cho 3rd party integrations)
-- =============================================================================

CREATE TABLE webhook_endpoints (
    id           SERIAL PRIMARY KEY,
    tenant_id    INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    name         VARCHAR(100) NOT NULL,
    url          VARCHAR(500) NOT NULL,
    secret_hash  VARCHAR(255),                         -- HMAC signing secret
    events       TEXT[]       NOT NULL DEFAULT '{}',
    -- e.g. '{booking.created, trip.departed, payment.success}'
    is_active    BOOLEAN      NOT NULL DEFAULT TRUE,
    timeout_sec  SMALLINT     NOT NULL DEFAULT 10,
    retry_count  SMALLINT     NOT NULL DEFAULT 3,
    headers      JSONB        NOT NULL DEFAULT '{}',   -- custom headers
    created_by   INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
SELECT create_updated_at_trigger('webhook_endpoints');

CREATE TABLE webhook_deliveries (
    id           BIGSERIAL PRIMARY KEY,
    endpoint_id  INTEGER      NOT NULL REFERENCES webhook_endpoints(id) ON DELETE CASCADE,
    event_type   VARCHAR(100) NOT NULL,
    payload      JSONB        NOT NULL,
    response_code SMALLINT,
    response_body TEXT,
    attempt      SMALLINT     NOT NULL DEFAULT 1,
    delivered_at TIMESTAMPTZ,
    failed_at    TIMESTAMPTZ,
    status       VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
    -- PENDING, SUCCESS, FAILED, RETRY
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_webhook_deliveries_endpoint ON webhook_deliveries(endpoint_id, status);
CREATE INDEX idx_webhook_deliveries_created  ON webhook_deliveries(created_at DESC);

-- =============================================================================
-- APP: tasks  (Công việc nội bộ / todo tracking)
-- =============================================================================

CREATE TABLE task_lists (
    id         SERIAL PRIMARY KEY,
    tenant_id  INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    name       VARCHAR(100) NOT NULL,
    branch_id  INTEGER      REFERENCES branches(id) ON DELETE SET NULL,
    created_by INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE tasks (
    id           BIGSERIAL PRIMARY KEY,
    tenant_id    INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    list_id      INTEGER      REFERENCES task_lists(id) ON DELETE SET NULL,
    title        VARCHAR(500) NOT NULL,
    description  TEXT,
    priority     VARCHAR(10)  NOT NULL DEFAULT 'MEDIUM',
    -- LOW, MEDIUM, HIGH, URGENT
    status       VARCHAR(20)  NOT NULL DEFAULT 'TODO',
    -- TODO, IN_PROGRESS, REVIEW, DONE, CANCELLED
    assignee_id  INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    created_by   INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    due_date     TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    entity_type  VARCHAR(60),                           -- liên kết tới trip, vehicle, ...
    entity_id    BIGINT,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_task_priority CHECK (priority IN ('LOW','MEDIUM','HIGH','URGENT')),
    CONSTRAINT chk_task_status   CHECK (status IN ('TODO','IN_PROGRESS','REVIEW','DONE','CANCELLED'))
);
SELECT create_updated_at_trigger('tasks');

CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_tasks_entity   ON tasks(entity_type, entity_id);
CREATE INDEX idx_tasks_status   ON tasks(status) WHERE status NOT IN ('DONE','CANCELLED');

-- =============================================================================
-- APP: comments  (Generic comment/note — gắn vào bất kỳ entity nào)
-- =============================================================================

CREATE TABLE comments (
    id           BIGSERIAL PRIMARY KEY,
    tenant_id    INTEGER     NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    entity_type  VARCHAR(60) NOT NULL,                 -- trip, booking, consignment, ...
    entity_id    BIGINT      NOT NULL,
    parent_id    BIGINT      REFERENCES comments(id) ON DELETE CASCADE,
    body         TEXT        NOT NULL,
    author_id    INTEGER     REFERENCES user_accounts(id) ON DELETE SET NULL,
    is_internal  BOOLEAN     NOT NULL DEFAULT TRUE,    -- FALSE = visible to customer
    is_pinned    BOOLEAN     NOT NULL DEFAULT FALSE,
    edited_at    TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_comments_entity ON comments(entity_type, entity_id);
CREATE INDEX idx_comments_parent ON comments(parent_id) WHERE parent_id IS NOT NULL;

-- =============================================================================
-- APP: routes
-- =============================================================================

CREATE TABLE provinces (
    id        SERIAL PRIMARY KEY,
    code      VARCHAR(10)  NOT NULL UNIQUE,
    name      VARCHAR(100) NOT NULL,
    region    VARCHAR(30)                              -- NORTH, CENTRAL, SOUTH
);

CREATE TABLE stations (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(20)  NOT NULL UNIQUE,
    name        VARCHAR(255) NOT NULL,
    province_id INTEGER      NOT NULL REFERENCES provinces(id),
    address     TEXT,
    latitude    NUMERIC(10,7),
    longitude   NUMERIC(10,7),
    phone       VARCHAR(20),
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
SELECT create_updated_at_trigger('stations');

CREATE TABLE routes (
    id              SERIAL PRIMARY KEY,
    tenant_id       INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    code            VARCHAR(20)  NOT NULL,
    name            VARCHAR(255) NOT NULL,
    origin_id       INTEGER      NOT NULL REFERENCES stations(id),
    destination_id  INTEGER      NOT NULL REFERENCES stations(id),
    distance_km     NUMERIC(8,2),
    duration_min    INTEGER,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, code)
);
SELECT create_updated_at_trigger('routes');

CREATE TABLE route_stops (
    id                SERIAL PRIMARY KEY,
    route_id          INTEGER  NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    station_id        INTEGER  NOT NULL REFERENCES stations(id),
    stop_order        SMALLINT NOT NULL,
    arrive_offset_min INTEGER,
    depart_offset_min INTEGER,
    pickup_allowed    BOOLEAN  NOT NULL DEFAULT TRUE,
    dropoff_allowed   BOOLEAN  NOT NULL DEFAULT TRUE,
    UNIQUE (route_id, stop_order)
);

-- =============================================================================
-- APP: vehicles
-- =============================================================================

CREATE TABLE vehicle_categories (
    id            SERIAL PRIMARY KEY,
    tenant_id     INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    code          VARCHAR(20)  NOT NULL,
    name          VARCHAR(100) NOT NULL,
    seat_count    SMALLINT     NOT NULL,
    vehicle_type  VARCHAR(50)  NOT NULL,
    -- BUS, SLEEPER_BUS, LIMOUSINE, MINIBUS
    description   TEXT,
    amenities     TEXT[],                              -- e.g. '{wifi,ac,usb}'
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, code),
    CONSTRAINT chk_vehicle_type CHECK (vehicle_type IN ('BUS','SLEEPER_BUS','LIMOUSINE','MINIBUS','OTHER'))
);
SELECT create_updated_at_trigger('vehicle_categories');

CREATE TABLE vehicles (
    id                  SERIAL PRIMARY KEY,
    tenant_id           INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    plate_number        VARCHAR(20)  NOT NULL UNIQUE,
    category_id         INTEGER      NOT NULL REFERENCES vehicle_categories(id),
    branch_id           INTEGER      REFERENCES branches(id) ON DELETE SET NULL,
    manufacture_year    SMALLINT,
    brand               VARCHAR(100),
    model               VARCHAR(100),
    color               VARCHAR(50),
    vin                 VARCHAR(50),                   -- Vehicle Identification Number
    status              VARCHAR(30)  NOT NULL DEFAULT 'AVAILABLE',
    -- AVAILABLE, IN_TRIP, MAINTENANCE, INACTIVE, DISPOSED
    odometer_km         NUMERIC(10,2),
    registration_expiry DATE,
    insurance_expiry    DATE,
    inspection_expiry   DATE,
    notes               TEXT,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_vehicle_status CHECK (status IN ('AVAILABLE','IN_TRIP','MAINTENANCE','INACTIVE','DISPOSED'))
);
SELECT create_updated_at_trigger('vehicles');

CREATE TABLE seat_maps (
    id              SERIAL PRIMARY KEY,
    category_id     INTEGER      NOT NULL REFERENCES vehicle_categories(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    total_seats     SMALLINT     NOT NULL,
    layout_config   JSONB        NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
SELECT create_updated_at_trigger('seat_maps');

CREATE TABLE seats (
    id           SERIAL PRIMARY KEY,
    seat_map_id  INTEGER     NOT NULL REFERENCES seat_maps(id) ON DELETE CASCADE,
    seat_code    VARCHAR(10) NOT NULL,
    seat_type    VARCHAR(30) NOT NULL DEFAULT 'SEAT',
    -- SEAT, BED, VIP, PREMIUM
    deck         SMALLINT    NOT NULL DEFAULT 1,
    row_num      SMALLINT,
    col_num      SMALLINT,
    position_x   NUMERIC(6,2),                        -- cho layout SVG
    position_y   NUMERIC(6,2),
    is_available BOOLEAN     NOT NULL DEFAULT TRUE,
    UNIQUE (seat_map_id, seat_code)
);

CREATE TABLE vehicle_maintenance (
    id            SERIAL PRIMARY KEY,
    vehicle_id    INTEGER      NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    type          VARCHAR(30)  NOT NULL,
    -- SCHEDULED, EMERGENCY, INSPECTION
    description   TEXT         NOT NULL,
    cost          NUMERIC(15,2),
    vendor        VARCHAR(255),
    odometer_in   NUMERIC(10,2),
    odometer_out  NUMERIC(10,2),
    scheduled_at  DATE,
    completed_at  DATE,
    performed_by  INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    status        VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
    -- PENDING, IN_PROGRESS, DONE, CANCELLED
    next_due_km   NUMERIC(10,2),
    next_due_date DATE,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_maintenance_type   CHECK (type IN ('SCHEDULED','EMERGENCY','INSPECTION','CLEANING')),
    CONSTRAINT chk_maintenance_status CHECK (status IN ('PENDING','IN_PROGRESS','DONE','CANCELLED'))
);
SELECT create_updated_at_trigger('vehicle_maintenance');

-- =============================================================================
-- APP: hr (human resources)
-- =============================================================================

CREATE TABLE departments (
    id         SERIAL PRIMARY KEY,
    tenant_id  INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    name       VARCHAR(100) NOT NULL,
    manager_id INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, name)
);

CREATE TABLE employees (
    id                  SERIAL PRIMARY KEY,
    tenant_id           INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    code                VARCHAR(20)  NOT NULL,
    full_name           VARCHAR(255) NOT NULL,
    national_id         VARCHAR(20),
    phone               VARCHAR(20),
    email               VARCHAR(254),
    date_of_birth       DATE,
    gender              VARCHAR(10),
    -- MALE, FEMALE, OTHER
    address             TEXT,
    position            VARCHAR(100) NOT NULL,
    -- DRIVER, ASSISTANT, CASHIER, DISPATCHER, ACCOUNTANT, MANAGER, OTHER
    department_id       INTEGER      REFERENCES departments(id) ON DELETE SET NULL,
    branch_id           INTEGER      REFERENCES branches(id) ON DELETE SET NULL,
    user_account_id     INTEGER UNIQUE REFERENCES user_accounts(id) ON DELETE SET NULL,
    hired_at            DATE         NOT NULL,
    terminated_at       DATE,
    termination_reason  TEXT,
    is_active           BOOLEAN      NOT NULL DEFAULT TRUE,
    -- Driver-specific
    license_number      VARCHAR(50),
    license_class       VARCHAR(10),
    license_expiry      DATE,
    -- Insurance
    social_insurance_no VARCHAR(20),
    health_insurance_no VARCHAR(20),
    tax_code            VARCHAR(20),
    bank_account        VARCHAR(30),
    bank_name           VARCHAR(100),
    emergency_contact   JSONB        NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, code),
    CONSTRAINT chk_employee_gender CHECK (gender IN ('MALE','FEMALE','OTHER'))
);
SELECT create_updated_at_trigger('employees');

CREATE TABLE shift_types (
    id         SERIAL PRIMARY KEY,
    tenant_id  INTEGER NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    code       VARCHAR(20)  NOT NULL,
    name       VARCHAR(100) NOT NULL,
    start_time TIME         NOT NULL,
    end_time   TIME         NOT NULL,
    is_overnight BOOLEAN    NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, code)
);
SELECT create_updated_at_trigger('shift_types');

CREATE TABLE attendances (
    id             SERIAL PRIMARY KEY,
    employee_id    INTEGER     NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    shift_type_id  INTEGER     REFERENCES shift_types(id) ON DELETE SET NULL,
    work_date      DATE        NOT NULL,
    check_in       TIMESTAMPTZ,
    check_out      TIMESTAMPTZ,
    check_in_lat   NUMERIC(10,7),
    check_in_lng   NUMERIC(10,7),
    status         VARCHAR(20) NOT NULL DEFAULT 'PRESENT',
    -- PRESENT, ABSENT, LATE, HALF_DAY, LEAVE, HOLIDAY
    notes          TEXT,
    approved_by    INTEGER     REFERENCES user_accounts(id) ON DELETE SET NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (employee_id, work_date)
);

CREATE TABLE leave_requests (
    id           SERIAL PRIMARY KEY,
    employee_id  INTEGER     NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    leave_type   VARCHAR(30) NOT NULL,
    -- ANNUAL, SICK, UNPAID, MATERNITY, COMPASSIONATE
    from_date    DATE        NOT NULL,
    to_date      DATE        NOT NULL,
    days_count   NUMERIC(4,1) NOT NULL,
    reason       TEXT,
    status       VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    -- PENDING, APPROVED, REJECTED, CANCELLED
    approved_by  INTEGER     REFERENCES user_accounts(id) ON DELETE SET NULL,
    approved_at  TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
SELECT create_updated_at_trigger('leave_requests');

CREATE TABLE payroll (
    id              SERIAL PRIMARY KEY,
    employee_id     INTEGER     NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    period_year     SMALLINT    NOT NULL,
    period_month    SMALLINT    NOT NULL,
    working_days    NUMERIC(4,1) NOT NULL DEFAULT 0,
    base_salary     NUMERIC(15,2) NOT NULL DEFAULT 0,
    allowances      NUMERIC(15,2) NOT NULL DEFAULT 0,
    overtime_pay    NUMERIC(15,2) NOT NULL DEFAULT 0,
    deductions      NUMERIC(15,2) NOT NULL DEFAULT 0,
    insurance_deduct NUMERIC(15,2) NOT NULL DEFAULT 0,
    tax_deduct      NUMERIC(15,2) NOT NULL DEFAULT 0,
    bonus           NUMERIC(15,2) NOT NULL DEFAULT 0,
    net_salary      NUMERIC(15,2) NOT NULL DEFAULT 0,
    status          VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
    -- DRAFT, APPROVED, PAID
    approved_by     INTEGER     REFERENCES user_accounts(id) ON DELETE SET NULL,
    paid_at         TIMESTAMPTZ,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (employee_id, period_year, period_month)
);
SELECT create_updated_at_trigger('payroll');

-- =============================================================================
-- APP: trips (schedule + dispatch)
-- =============================================================================

CREATE TABLE trip_schedules (
    id              SERIAL PRIMARY KEY,
    tenant_id       INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    code            VARCHAR(30)  NOT NULL,
    route_id        INTEGER      NOT NULL REFERENCES routes(id),
    departure_time  TIME         NOT NULL,
    arrival_time    TIME,
    days_of_week    SMALLINT[]   NOT NULL DEFAULT '{1,2,3,4,5,6,7}',
    category_id     INTEGER      REFERENCES vehicle_categories(id) ON DELETE SET NULL,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    valid_from      DATE,
    valid_to        DATE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, code)
);
SELECT create_updated_at_trigger('trip_schedules');

CREATE TABLE trips (
    id                 SERIAL PRIMARY KEY,
    tenant_id          INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    code               VARCHAR(30)  NOT NULL,
    schedule_id        INTEGER      REFERENCES trip_schedules(id) ON DELETE SET NULL,
    route_id           INTEGER      NOT NULL REFERENCES routes(id),
    vehicle_id         INTEGER      REFERENCES vehicles(id) ON DELETE SET NULL,
    seat_map_id        INTEGER      REFERENCES seat_maps(id) ON DELETE SET NULL,
    departure_time     TIMESTAMPTZ  NOT NULL,
    estimated_arrival  TIMESTAMPTZ,
    actual_departure   TIMESTAMPTZ,
    actual_arrival     TIMESTAMPTZ,
    status             VARCHAR(30)  NOT NULL DEFAULT 'SCHEDULED',
    -- SCHEDULED, BOARDING, DEPARTED, ARRIVED, CANCELLED, DELAYED, DIVERTED
    cancel_reason      TEXT,
    delay_reason       TEXT,
    branch_id          INTEGER      REFERENCES branches(id) ON DELETE SET NULL,
    notes              TEXT,
    created_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, code),
    CONSTRAINT chk_trip_status CHECK (status IN (
        'SCHEDULED','BOARDING','DEPARTED','ARRIVED','CANCELLED','DELAYED','DIVERTED'))
);
SELECT create_updated_at_trigger('trips');

CREATE TABLE trip_staff (
    id            SERIAL PRIMARY KEY,
    trip_id       INTEGER     NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    employee_id   INTEGER     NOT NULL REFERENCES employees(id),
    role          VARCHAR(30) NOT NULL,
    -- DRIVER, ASSISTANT, INSPECTOR
    shift_type_id INTEGER     REFERENCES shift_types(id) ON DELETE SET NULL,
    confirmed     BOOLEAN     NOT NULL DEFAULT FALSE,
    UNIQUE (trip_id, employee_id)
);

CREATE TABLE trip_prices (
    id          SERIAL PRIMARY KEY,
    tenant_id   INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    route_id    INTEGER      NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    seat_type   VARCHAR(30)  NOT NULL DEFAULT 'SEAT',
    price       NUMERIC(15,2) NOT NULL,
    child_price NUMERIC(15,2),                        -- Giá trẻ em
    valid_from  DATE         NOT NULL,
    valid_to    DATE,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
SELECT create_updated_at_trigger('trip_prices');

CREATE TABLE dispatch_orders (
    id           SERIAL PRIMARY KEY,
    trip_id      INTEGER     NOT NULL UNIQUE REFERENCES trips(id),
    issued_by    INTEGER     REFERENCES user_accounts(id) ON DELETE SET NULL,
    issued_at    TIMESTAMPTZ,
    checklist    JSONB       NOT NULL DEFAULT '{}',   -- pre-departure checklist
    notes        TEXT,
    status       VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    -- PENDING, ISSUED, DEPARTED
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Trip tracking (GPS / trạng thái theo thời gian thực)
CREATE TABLE trip_tracking (
    id          BIGSERIAL PRIMARY KEY,
    trip_id     INTEGER     NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    latitude    NUMERIC(10,7) NOT NULL,
    longitude   NUMERIC(10,7) NOT NULL,
    speed_kmh   NUMERIC(6,2),
    heading     NUMERIC(5,2),
    event_type  VARCHAR(30),
    -- LOCATION, STOP, START, BREAKDOWN, ARRIVAL
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (recorded_at);

CREATE TABLE trip_tracking_2025 PARTITION OF trip_tracking
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE trip_tracking_2026 PARTITION OF trip_tracking
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

CREATE INDEX idx_trip_tracking_trip ON trip_tracking(trip_id, recorded_at DESC);

-- =============================================================================
-- APP: customers & tickets
-- =============================================================================

CREATE TABLE customers (
    id          SERIAL PRIMARY KEY,
    tenant_id   INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    uuid        UUID         NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    full_name   VARCHAR(255) NOT NULL,
    phone       VARCHAR(20)  NOT NULL,
    email       VARCHAR(254),
    national_id VARCHAR(20),
    date_of_birth DATE,
    gender      VARCHAR(10),
    address     TEXT,
    loyalty_points INTEGER    NOT NULL DEFAULT 0,
    tier        VARCHAR(20)  NOT NULL DEFAULT 'STANDARD',
    -- STANDARD, SILVER, GOLD, PLATINUM
    notes       TEXT,
    source      VARCHAR(30)  NOT NULL DEFAULT 'COUNTER',
    -- COUNTER, ONLINE, AGENT, IMPORT
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, phone)
);
SELECT create_updated_at_trigger('customers');

CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_email ON customers(email) WHERE email IS NOT NULL;
CREATE INDEX idx_customers_name  ON customers USING gin (full_name gin_trgm_ops);

CREATE TABLE ticket_bookings (
    id            BIGSERIAL PRIMARY KEY,
    tenant_id     INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    booking_code  VARCHAR(30)  NOT NULL UNIQUE,
    customer_id   INTEGER      NOT NULL REFERENCES customers(id),
    trip_id       INTEGER      NOT NULL REFERENCES trips(id),
    booked_by     INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    branch_id     INTEGER      REFERENCES branches(id) ON DELETE SET NULL,
    channel       VARCHAR(30)  NOT NULL DEFAULT 'COUNTER',
    -- COUNTER, ONLINE, AGENT, MOBILE_APP, B2B
    status        VARCHAR(30)  NOT NULL DEFAULT 'PENDING',
    -- PENDING, CONFIRMED, CANCELLED, REFUNDED, NO_SHOW
    total_amount  NUMERIC(15,2) NOT NULL DEFAULT 0,
    paid_amount   NUMERIC(15,2) NOT NULL DEFAULT 0,
    note          TEXT,
    cancelled_at  TIMESTAMPTZ,
    cancel_reason TEXT,
    expires_at    TIMESTAMPTZ,                         -- hold expiry
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_booking_status  CHECK (status IN ('PENDING','CONFIRMED','CANCELLED','REFUNDED','NO_SHOW')),
    CONSTRAINT chk_booking_channel CHECK (channel IN ('COUNTER','ONLINE','AGENT','MOBILE_APP','B2B'))
);
SELECT create_updated_at_trigger('ticket_bookings');

CREATE INDEX idx_bookings_trip      ON ticket_bookings(trip_id);
CREATE INDEX idx_bookings_customer  ON ticket_bookings(customer_id);
CREATE INDEX idx_bookings_status    ON ticket_bookings(status);
CREATE INDEX idx_bookings_channel   ON ticket_bookings(channel);
CREATE INDEX idx_bookings_created   ON ticket_bookings(created_at DESC);

CREATE TABLE tickets (
    id              BIGSERIAL PRIMARY KEY,
    booking_id      BIGINT      NOT NULL REFERENCES ticket_bookings(id) ON DELETE CASCADE,
    seat_id         INTEGER     REFERENCES seats(id) ON DELETE SET NULL,
    seat_code       VARCHAR(10),                       -- snapshot
    passenger_name  VARCHAR(255),
    passenger_phone VARCHAR(20),
    passenger_type  VARCHAR(20) NOT NULL DEFAULT 'ADULT',
    -- ADULT, CHILD, INFANT, STUDENT, SENIOR
    base_price      NUMERIC(15,2) NOT NULL,
    discount_amount NUMERIC(15,2) NOT NULL DEFAULT 0,
    final_price     NUMERIC(15,2) NOT NULL,
    qr_code         VARCHAR(100) UNIQUE,               -- QR token
    barcode         VARCHAR(100) UNIQUE,
    status          VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    -- ACTIVE, USED, CANCELLED, REFUNDED, EXCHANGED, EXPIRED
    checked_in_at   TIMESTAMPTZ,
    checked_in_by   INTEGER     REFERENCES user_accounts(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_ticket_status CHECK (status IN ('ACTIVE','USED','CANCELLED','REFUNDED','EXCHANGED','EXPIRED'))
);
SELECT create_updated_at_trigger('tickets');

CREATE INDEX idx_tickets_booking ON tickets(booking_id);
CREATE INDEX idx_tickets_status  ON tickets(status);
CREATE INDEX idx_tickets_qr      ON tickets(qr_code) WHERE qr_code IS NOT NULL;

CREATE TABLE ticket_refunds (
    id              BIGSERIAL PRIMARY KEY,
    ticket_id       BIGINT      NOT NULL REFERENCES tickets(id),
    refund_code     VARCHAR(30) NOT NULL UNIQUE,
    reason          TEXT,
    original_amount NUMERIC(15,2) NOT NULL,
    penalty_amount  NUMERIC(15,2) NOT NULL DEFAULT 0,
    refund_amount   NUMERIC(15,2) NOT NULL,
    refund_method   VARCHAR(30),
    -- CASH, BANK_TRANSFER, WALLET, CREDIT
    processed_by    INTEGER     REFERENCES user_accounts(id) ON DELETE SET NULL,
    approved_by     INTEGER     REFERENCES user_accounts(id) ON DELETE SET NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    -- PENDING, APPROVED, COMPLETED, REJECTED
    processed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
SELECT create_updated_at_trigger('ticket_refunds');

CREATE TABLE ticket_exchanges (
    id                 BIGSERIAL PRIMARY KEY,
    original_ticket_id BIGINT      NOT NULL REFERENCES tickets(id),
    new_ticket_id      BIGINT      REFERENCES tickets(id) ON DELETE SET NULL,
    exchange_code      VARCHAR(30) NOT NULL UNIQUE,
    reason             TEXT,
    fee                NUMERIC(15,2) NOT NULL DEFAULT 0,
    processed_by       INTEGER     REFERENCES user_accounts(id) ON DELETE SET NULL,
    status             VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE group_contracts (
    id               SERIAL PRIMARY KEY,
    tenant_id        INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    contract_code    VARCHAR(30)  NOT NULL UNIQUE,
    customer_name    VARCHAR(255) NOT NULL,
    customer_phone   VARCHAR(20)  NOT NULL,
    customer_email   VARCHAR(254),
    customer_tax_code VARCHAR(20),
    trip_id          INTEGER      NOT NULL REFERENCES trips(id),
    seat_count       SMALLINT     NOT NULL,
    total_amount     NUMERIC(15,2) NOT NULL,
    deposit_amount   NUMERIC(15,2) NOT NULL DEFAULT 0,
    deposit_paid_at  TIMESTAMPTZ,
    status           VARCHAR(30)  NOT NULL DEFAULT 'DRAFT',
    -- DRAFT, CONFIRMED, CANCELLED, COMPLETED
    contract_file    VARCHAR(500),
    notes            TEXT,
    created_by       INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
SELECT create_updated_at_trigger('group_contracts');

-- =============================================================================
-- APP: payments
-- =============================================================================

CREATE TABLE payment_methods (
    id         SERIAL PRIMARY KEY,
    tenant_id  INTEGER     NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    code       VARCHAR(30) NOT NULL,
    -- CASH, CARD, MOMO, VNPAY, ZALOPAY, BANK_TRANSFER, CREDIT
    name       VARCHAR(100) NOT NULL,
    provider   VARCHAR(50),                           -- gateway provider
    config     JSONB       NOT NULL DEFAULT '{}',     -- API keys, endpoints (encrypted)
    sort_order SMALLINT    NOT NULL DEFAULT 0,
    is_active  BOOLEAN     NOT NULL DEFAULT TRUE,
    UNIQUE (tenant_id, code)
);

CREATE TABLE payments (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    payment_code    VARCHAR(30)  NOT NULL UNIQUE,
    booking_id      BIGINT       REFERENCES ticket_bookings(id) ON DELETE SET NULL,
    consignment_id  BIGINT,                           -- FK added after consignments
    amount          NUMERIC(15,2) NOT NULL,
    method_id       INTEGER      NOT NULL REFERENCES payment_methods(id),
    status          VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
    -- PENDING, SUCCESS, FAILED, REFUNDED, EXPIRED
    transaction_ref VARCHAR(100),
    gateway_response JSONB       NOT NULL DEFAULT '{}',
    cashier_id      INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    branch_id       INTEGER      REFERENCES branches(id) ON DELETE SET NULL,
    paid_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_payment_status CHECK (status IN ('PENDING','SUCCESS','FAILED','REFUNDED','EXPIRED'))
);
SELECT create_updated_at_trigger('payments');

CREATE INDEX idx_payments_booking ON payments(booking_id);
CREATE INDEX idx_payments_status  ON payments(status);
CREATE INDEX idx_payments_paid_at ON payments(paid_at DESC);

CREATE TABLE cashier_sessions (
    id             SERIAL PRIMARY KEY,
    tenant_id      INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    cashier_id     INTEGER      NOT NULL REFERENCES user_accounts(id),
    branch_id      INTEGER      NOT NULL REFERENCES branches(id),
    opened_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    closed_at      TIMESTAMPTZ,
    opening_cash   NUMERIC(15,2) NOT NULL DEFAULT 0,
    closing_cash   NUMERIC(15,2),
    total_sales    NUMERIC(15,2),
    total_refunds  NUMERIC(15,2),
    discrepancy    NUMERIC(15,2),
    status         VARCHAR(20)  NOT NULL DEFAULT 'OPEN',
    -- OPEN, CLOSED, RECONCILED
    notes          TEXT,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE invoices (
    id                SERIAL PRIMARY KEY,
    tenant_id         INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    invoice_no        VARCHAR(50)  NOT NULL UNIQUE,
    series            VARCHAR(10)  NOT NULL,
    booking_id        BIGINT       REFERENCES ticket_bookings(id) ON DELETE SET NULL,
    group_contract_id INTEGER      REFERENCES group_contracts(id) ON DELETE SET NULL,
    buyer_name        VARCHAR(255),
    buyer_tax_code    VARCHAR(20),
    buyer_address     TEXT,
    buyer_email       VARCHAR(254),
    subtotal          NUMERIC(15,2) NOT NULL,
    vat_rate          NUMERIC(5,2)  NOT NULL DEFAULT 10.00,
    vat_amount        NUMERIC(15,2) NOT NULL,
    total_amount      NUMERIC(15,2) NOT NULL,
    status            VARCHAR(20)  NOT NULL DEFAULT 'DRAFT',
    -- DRAFT, ISSUED, CANCELLED, REPLACED
    e_invoice_code    VARCHAR(100),
    e_invoice_url     VARCHAR(500),
    issued_at         TIMESTAMPTZ,
    issued_by         INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
SELECT create_updated_at_trigger('invoices');

-- =============================================================================
-- APP: consignments (cargo/hàng hoá)
-- =============================================================================

CREATE TABLE cargo_price_tables (
    id           SERIAL PRIMARY KEY,
    tenant_id    INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    route_id     INTEGER      REFERENCES routes(id) ON DELETE SET NULL,
    cargo_type   VARCHAR(50),
    -- NORMAL, FRAGILE, LIQUID, FROZEN, OVERSIZED, HAZARDOUS
    min_weight   NUMERIC(8,2),
    max_weight   NUMERIC(8,2),
    min_volume   NUMERIC(8,3),
    max_volume   NUMERIC(8,3),
    price        NUMERIC(15,2) NOT NULL,
    price_unit   VARCHAR(20)  NOT NULL DEFAULT 'PER_KG',
    -- PER_KG, PER_TRIP, FLAT, PER_M3
    is_active    BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
SELECT create_updated_at_trigger('cargo_price_tables');

CREATE TABLE consignments (
    id                     BIGSERIAL PRIMARY KEY,
    tenant_id              INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    waybill_code           VARCHAR(30)  NOT NULL UNIQUE,
    barcode                VARCHAR(100) UNIQUE,
    qr_code                VARCHAR(100) UNIQUE,
    trip_id                INTEGER      REFERENCES trips(id) ON DELETE SET NULL,
    sender_name            VARCHAR(255) NOT NULL,
    sender_phone           VARCHAR(20)  NOT NULL,
    receiver_name          VARCHAR(255) NOT NULL,
    receiver_phone         VARCHAR(20)  NOT NULL,
    origin_station_id      INTEGER      REFERENCES stations(id) ON DELETE SET NULL,
    destination_station_id INTEGER      REFERENCES stations(id) ON DELETE SET NULL,
    cargo_type             VARCHAR(50),
    description            TEXT,
    weight_kg              NUMERIC(8,2),
    volume_m3              NUMERIC(8,3),
    declared_value         NUMERIC(15,2),
    freight_charge         NUMERIC(15,2) NOT NULL DEFAULT 0,
    insurance_fee          NUMERIC(15,2) NOT NULL DEFAULT 0,
    cod_amount             NUMERIC(15,2) NOT NULL DEFAULT 0,
    cod_collected          BOOLEAN      NOT NULL DEFAULT FALSE,
    cod_transferred        BOOLEAN      NOT NULL DEFAULT FALSE,
    status                 VARCHAR(30)  NOT NULL DEFAULT 'RECEIVED',
    -- RECEIVED, LOADED, IN_TRANSIT, ARRIVED, DELIVERED, RETURNED, LOST, DAMAGED
    received_by            INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    delivered_by           INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    received_at            TIMESTAMPTZ,
    delivered_at           TIMESTAMPTZ,
    branch_id              INTEGER      REFERENCES branches(id) ON DELETE SET NULL,
    notes                  TEXT,
    created_at             TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_consignment_status CHECK (status IN (
        'RECEIVED','LOADED','IN_TRANSIT','ARRIVED','DELIVERED','RETURNED','LOST','DAMAGED'))
);
SELECT create_updated_at_trigger('consignments');

CREATE INDEX idx_consignments_status ON consignments(status);
CREATE INDEX idx_consignments_trip   ON consignments(trip_id);
CREATE INDEX idx_consignments_sender ON consignments(sender_phone);
CREATE INDEX idx_consignments_recv   ON consignments(receiver_phone);

-- Lịch sử trạng thái hàng hoá
CREATE TABLE consignment_events (
    id             BIGSERIAL PRIMARY KEY,
    consignment_id BIGINT      NOT NULL REFERENCES consignments(id) ON DELETE CASCADE,
    event_type     VARCHAR(30) NOT NULL,
    -- STATUS_CHANGE, NOTE, SCAN, PHOTO
    old_status     VARCHAR(30),
    new_status     VARCHAR(30),
    description    TEXT,
    location       VARCHAR(255),
    recorded_by    INTEGER     REFERENCES user_accounts(id) ON DELETE SET NULL,
    recorded_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_consignment_events ON consignment_events(consignment_id, recorded_at DESC);

CREATE TABLE consignment_manifests (
    id             SERIAL PRIMARY KEY,
    manifest_code  VARCHAR(30) NOT NULL UNIQUE,
    trip_id        INTEGER     NOT NULL REFERENCES trips(id),
    created_by     INTEGER     REFERENCES user_accounts(id) ON DELETE SET NULL,
    status         VARCHAR(20) NOT NULL DEFAULT 'OPEN',
    -- OPEN, CLOSED, DISPATCHED
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE manifest_items (
    id             SERIAL PRIMARY KEY,
    manifest_id    INTEGER NOT NULL REFERENCES consignment_manifests(id) ON DELETE CASCADE,
    consignment_id BIGINT  NOT NULL REFERENCES consignments(id),
    loaded_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (manifest_id, consignment_id)
);

CREATE TABLE cod_reconciliations (
    id             SERIAL PRIMARY KEY,
    consignment_id BIGINT       NOT NULL REFERENCES consignments(id),
    amount         NUMERIC(15,2) NOT NULL,
    transferred_by INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    transferred_at TIMESTAMPTZ,
    status         VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
    -- PENDING, TRANSFERRED, CONFIRMED
    notes          TEXT,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

ALTER TABLE payments
    ADD CONSTRAINT fk_payment_consignment FOREIGN KEY (consignment_id)
    REFERENCES consignments(id) ON DELETE SET NULL;

-- =============================================================================
-- APP: promotions & loyalty
-- =============================================================================

CREATE TABLE promotions (
    id                    SERIAL PRIMARY KEY,
    tenant_id             INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    code                  VARCHAR(50)  NOT NULL,
    name                  VARCHAR(255) NOT NULL,
    description           TEXT,
    discount_type         VARCHAR(20)  NOT NULL,
    -- PERCENT, FIXED_AMOUNT, FREE_SEAT
    discount_value        NUMERIC(10,2) NOT NULL,
    min_order_amount      NUMERIC(15,2),
    max_discount          NUMERIC(15,2),
    usage_limit           INTEGER,
    usage_limit_per_user  INTEGER,
    usage_count           INTEGER      NOT NULL DEFAULT 0,
    applicable_routes     INTEGER[],
    applicable_seat_types VARCHAR(30)[],
    applicable_channels   VARCHAR(30)[],
    valid_from            TIMESTAMPTZ  NOT NULL,
    valid_to              TIMESTAMPTZ,
    is_active             BOOLEAN      NOT NULL DEFAULT TRUE,
    created_by            INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, code),
    CONSTRAINT chk_promotion_type CHECK (discount_type IN ('PERCENT','FIXED_AMOUNT','FREE_SEAT'))
);
SELECT create_updated_at_trigger('promotions');

CREATE TABLE promotion_usages (
    id               BIGSERIAL PRIMARY KEY,
    promotion_id     INTEGER      NOT NULL REFERENCES promotions(id),
    booking_id       BIGINT       NOT NULL REFERENCES ticket_bookings(id),
    customer_id      INTEGER      REFERENCES customers(id) ON DELETE SET NULL,
    discount_applied NUMERIC(15,2) NOT NULL,
    used_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE loyalty_transactions (
    id           BIGSERIAL PRIMARY KEY,
    customer_id  INTEGER      NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    booking_id   BIGINT       REFERENCES ticket_bookings(id) ON DELETE SET NULL,
    type         VARCHAR(20)  NOT NULL,
    -- EARN, REDEEM, EXPIRE, ADJUST
    points       INTEGER      NOT NULL,
    balance      INTEGER      NOT NULL,
    description  TEXT,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE after_sales (
    id          SERIAL PRIMARY KEY,
    tenant_id   INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    code        VARCHAR(50)  NOT NULL,
    name        VARCHAR(255) NOT NULL,
    description TEXT,
    type        VARCHAR(30)  NOT NULL,
    -- VOUCHER, LOYALTY_POINTS, GIFT, DISCOUNT_CODE
    value       NUMERIC(10,2),
    conditions  JSONB        NOT NULL DEFAULT '{}',
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_by  INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, code)
);
SELECT create_updated_at_trigger('after_sales');

-- =============================================================================
-- APP: notifications
-- =============================================================================

CREATE TABLE notification_templates (
    id         SERIAL PRIMARY KEY,
    tenant_id  INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    code       VARCHAR(50)  NOT NULL,
    name       VARCHAR(255) NOT NULL,
    channel    VARCHAR(20)  NOT NULL,
    -- SMS, EMAIL, PUSH, ZALO, IN_APP
    subject    VARCHAR(500),
    body       TEXT         NOT NULL,
    variables  TEXT[],                                -- list of available {variables}
    is_active  BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, code, channel)
);
SELECT create_updated_at_trigger('notification_templates');

CREATE TABLE notifications (
    id               BIGSERIAL PRIMARY KEY,
    tenant_id        INTEGER      NOT NULL DEFAULT 1,
    template_id      INTEGER      REFERENCES notification_templates(id) ON DELETE SET NULL,
    recipient_type   VARCHAR(20)  NOT NULL,
    -- USER, CUSTOMER, EMPLOYEE
    recipient_id     INTEGER,
    recipient_phone  VARCHAR(20),
    recipient_email  VARCHAR(254),
    channel          VARCHAR(20)  NOT NULL,
    subject          VARCHAR(500),
    body             TEXT         NOT NULL,
    status           VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
    -- PENDING, SENT, FAILED, CANCELLED
    retry_count      SMALLINT     NOT NULL DEFAULT 0,
    sent_at          TIMESTAMPTZ,
    error_msg        TEXT,
    ref_type         VARCHAR(60),                     -- booking, trip, consignment
    ref_id           BIGINT,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (created_at);

CREATE TABLE notifications_2025 PARTITION OF notifications
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE notifications_2026 PARTITION OF notifications
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

CREATE INDEX idx_notifications_status  ON notifications(status, created_at);
CREATE INDEX idx_notifications_ref     ON notifications(ref_type, ref_id);

-- =============================================================================
-- APP: financials (chi phí + báo cáo)
-- =============================================================================

CREATE TABLE expense_categories (
    id         SERIAL PRIMARY KEY,
    tenant_id  INTEGER     NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    code       VARCHAR(30) NOT NULL,
    name       VARCHAR(100) NOT NULL,
    parent_id  INTEGER     REFERENCES expense_categories(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, code)
);

CREATE TABLE expenses (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    category_id     INTEGER      NOT NULL REFERENCES expense_categories(id),
    vehicle_id      INTEGER      REFERENCES vehicles(id) ON DELETE SET NULL,
    trip_id         INTEGER      REFERENCES trips(id) ON DELETE SET NULL,
    branch_id       INTEGER      REFERENCES branches(id) ON DELETE SET NULL,
    employee_id     INTEGER      REFERENCES employees(id) ON DELETE SET NULL,
    title           VARCHAR(255) NOT NULL,
    amount          NUMERIC(15,2) NOT NULL,
    expense_date    DATE         NOT NULL,
    description     TEXT,
    attachment      VARCHAR(500),
    submitted_by    INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    approved_by     INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    status          VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
    -- PENDING, APPROVED, REJECTED, PAID
    approved_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
SELECT create_updated_at_trigger('expenses');

CREATE INDEX idx_expenses_date     ON expenses(expense_date);
CREATE INDEX idx_expenses_branch   ON expenses(branch_id, expense_date);
CREATE INDEX idx_expenses_vehicle  ON expenses(vehicle_id) WHERE vehicle_id IS NOT NULL;

CREATE TABLE fuel_allocations (
    id               SERIAL PRIMARY KEY,
    vehicle_id       INTEGER      NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    trip_id          INTEGER      REFERENCES trips(id) ON DELETE SET NULL,
    driver_id        INTEGER      REFERENCES employees(id) ON DELETE SET NULL,
    liters           NUMERIC(8,2) NOT NULL,
    price_per_liter  NUMERIC(10,2) NOT NULL,
    total_cost       NUMERIC(15,2) NOT NULL,
    station_name     VARCHAR(255),
    odometer         NUMERIC(10,2),
    allocated_by     INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    allocated_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    notes            TEXT,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_fuel_vehicle ON fuel_allocations(vehicle_id, allocated_at DESC);

-- =============================================================================
-- APP: assets (tài sản cố định)
-- =============================================================================

CREATE TABLE asset_categories (
    id         SERIAL PRIMARY KEY,
    tenant_id  INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    name       VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, name)
);

CREATE TABLE assets (
    id                SERIAL PRIMARY KEY,
    tenant_id         INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    code              VARCHAR(30)  NOT NULL,
    name              VARCHAR(255) NOT NULL,
    category_id       INTEGER      REFERENCES asset_categories(id) ON DELETE SET NULL,
    branch_id         INTEGER      REFERENCES branches(id) ON DELETE SET NULL,
    assigned_to       INTEGER      REFERENCES employees(id) ON DELETE SET NULL,
    serial_number     VARCHAR(100),
    purchase_date     DATE,
    purchase_price    NUMERIC(15,2),
    depreciation_rate NUMERIC(5,2),                   -- % per year
    current_value     NUMERIC(15,2),
    warranty_expiry   DATE,
    status            VARCHAR(30)  NOT NULL DEFAULT 'IN_USE',
    -- IN_USE, MAINTENANCE, DISPOSED, LOST, TRANSFERRED
    notes             TEXT,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, code)
);
SELECT create_updated_at_trigger('assets');

CREATE TABLE storage_units (
    id          SERIAL PRIMARY KEY,
    tenant_id   INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    code        VARCHAR(30)  NOT NULL,
    name        VARCHAR(100) NOT NULL,
    branch_id   INTEGER      REFERENCES branches(id) ON DELETE SET NULL,
    description TEXT,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, code)
);
SELECT create_updated_at_trigger('storage_units');

-- =============================================================================
-- APP: reports (saved report definitions)
-- =============================================================================

CREATE TABLE report_definitions (
    id           SERIAL PRIMARY KEY,
    tenant_id    INTEGER      NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    code         VARCHAR(60)  NOT NULL,
    name         VARCHAR(255) NOT NULL,
    category     VARCHAR(60)  NOT NULL,
    -- REVENUE, OPERATIONS, HR, CARGO, CUSTOMERS
    description  TEXT,
    query_config JSONB        NOT NULL DEFAULT '{}',  -- filters, dimensions, metrics
    chart_config JSONB        NOT NULL DEFAULT '{}',
    is_builtin   BOOLEAN      NOT NULL DEFAULT FALSE,
    is_public    BOOLEAN      NOT NULL DEFAULT FALSE,
    created_by   INTEGER      REFERENCES user_accounts(id) ON DELETE SET NULL,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, code)
);
SELECT create_updated_at_trigger('report_definitions');

CREATE TABLE scheduled_reports (
    id             SERIAL PRIMARY KEY,
    report_id      INTEGER      NOT NULL REFERENCES report_definitions(id) ON DELETE CASCADE,
    name           VARCHAR(100) NOT NULL,
    frequency      VARCHAR(20)  NOT NULL,
    -- DAILY, WEEKLY, MONTHLY
    cron_expr      VARCHAR(50),
    recipients     JSONB        NOT NULL DEFAULT '[]',
    -- [{type: email|user, value}]
    format         VARCHAR(10)  NOT NULL DEFAULT 'PDF',
    -- PDF, EXCEL, CSV
    last_run_at    TIMESTAMPTZ,
    next_run_at    TIMESTAMPTZ,
    is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- ADDITIONAL INDEXES
-- =============================================================================

CREATE INDEX idx_trips_departure   ON trips(departure_time);
CREATE INDEX idx_trips_status      ON trips(status);
CREATE INDEX idx_trips_route       ON trips(route_id);
CREATE INDEX idx_trips_vehicle     ON trips(vehicle_id) WHERE vehicle_id IS NOT NULL;
CREATE INDEX idx_trips_branch      ON trips(branch_id, departure_time);

CREATE INDEX idx_vehicles_status   ON vehicles(status);
CREATE INDEX idx_vehicles_branch   ON vehicles(branch_id);
CREATE INDEX idx_vehicles_plate    ON vehicles USING gin (plate_number gin_trgm_ops);

CREATE INDEX idx_employees_branch  ON employees(branch_id);
CREATE INDEX idx_employees_pos     ON employees(position);
CREATE INDEX idx_employees_name    ON employees USING gin (full_name gin_trgm_ops);

CREATE INDEX idx_config_category   ON system_configs(tenant_id, category);
CREATE INDEX idx_config_public     ON system_configs(is_public) WHERE is_public = TRUE;

CREATE INDEX idx_feature_flags     ON feature_flags(tenant_id, key);

CREATE INDEX idx_menu_items_perm   ON menu_items(permission_code) WHERE permission_code IS NOT NULL;

-- GIN indexes cho JSONB search
CREATE INDEX idx_payroll_jsonb         ON payroll USING gin ((to_jsonb(payroll.*)));
CREATE INDEX idx_consignment_gin       ON consignments USING gin (notes gin_trgm_ops)
    WHERE notes IS NOT NULL;
CREATE INDEX idx_audit_changes_gin     ON audit_logs USING gin (changes)
    WHERE changes IS NOT NULL;

-- =============================================================================
-- VIEWS tiện dụng
-- =============================================================================

CREATE VIEW v_trip_summary AS
SELECT
    t.id,
    t.code,
    t.departure_time,
    t.status,
    r.name            AS route_name,
    v.plate_number,
    COUNT(tb.id)      AS booking_count,
    COUNT(tk.id)      AS ticket_count,
    SUM(tk.final_price) FILTER (WHERE tk.status = 'ACTIVE') AS revenue
FROM trips t
LEFT JOIN routes r           ON r.id = t.route_id
LEFT JOIN vehicles v         ON v.id = t.vehicle_id
LEFT JOIN ticket_bookings tb ON tb.trip_id = t.id AND tb.status = 'CONFIRMED'
LEFT JOIN tickets tk         ON tk.booking_id = tb.id
GROUP BY t.id, r.name, v.plate_number;

CREATE VIEW v_vehicle_status AS
SELECT
    v.id,
    v.plate_number,
    vc.name AS category,
    b.name  AS branch,
    v.status,
    v.registration_expiry,
    v.insurance_expiry,
    v.inspection_expiry,
    CASE
        WHEN v.registration_expiry < CURRENT_DATE + 30 THEN 'EXPIRING_SOON'
        WHEN v.insurance_expiry     < CURRENT_DATE + 30 THEN 'EXPIRING_SOON'
        ELSE 'OK'
    END AS compliance_status
FROM vehicles v
LEFT JOIN vehicle_categories vc ON vc.id = v.category_id
LEFT JOIN branches b            ON b.id  = v.branch_id;

CREATE VIEW v_daily_revenue AS
SELECT
    DATE(p.paid_at)      AS revenue_date,
    b.name               AS branch,
    pm.name              AS payment_method,
    COUNT(p.id)          AS transaction_count,
    SUM(p.amount)        AS total_amount
FROM payments p
LEFT JOIN branches b        ON b.id  = p.branch_id
LEFT JOIN payment_methods pm ON pm.id = p.method_id
WHERE p.status = 'SUCCESS'
GROUP BY DATE(p.paid_at), b.name, pm.name;

-- =============================================================================
-- SEED DATA: Permissions gắn với menu sidebar
-- =============================================================================

INSERT INTO permissions (codename, name, module, action) VALUES
-- Dashboard
('dashboard.view',                'Xem Dashboard',              'dashboard',     'view'),
-- Điều hành vé
('tickets.view',                  'Xem vé',                     'tickets',       'view'),
('tickets.add',                   'Thêm vé / Đặt vé nhanh',     'tickets',       'add'),
('tickets.change',                'Sửa vé',                     'tickets',       'change'),
('tickets.delete',                'Hủy vé',                     'tickets',       'delete'),
('tickets.export',                'Xuất danh sách vé',          'tickets',       'export'),
('bookings.view',                 'Xem phiếu đặt',              'tickets',       'view'),
('bookings.refund',               'Hoàn vé',                    'tickets',       'approve'),
('bookings.exchange',             'Đổi vé',                     'tickets',       'change'),
-- Lịch trình
('trips.view',                    'Xem chuyến xe',              'trips',         'view'),
('trips.add',                     'Tạo chuyến xe',              'trips',         'add'),
('trips.change',                  'Sửa chuyến xe',              'trips',         'change'),
('trips.dispatch',                'Điều phối / xuất bến',       'trips',         'approve'),
('trip_prices.view',              'Xem bảng giá vé',            'trips',         'view'),
('trip_prices.change',            'Sửa bảng giá vé',            'trips',         'change'),
-- Quản lý đội xe
('vehicles.view',                 'Xem đội xe',                 'vehicles',      'view'),
('vehicles.add',                  'Thêm xe',                    'vehicles',      'add'),
('vehicles.change',               'Sửa thông tin xe',           'vehicles',      'change'),
('vehicles.maintenance',          'Quản lý bảo dưỡng',          'vehicles',      'change'),
-- Hàng hoá
('consignments.view',             'Xem vận đơn',                'consignments',  'view'),
('consignments.add',              'Tạo vận đơn',                'consignments',  'add'),
('consignments.change',           'Cập nhật vận đơn',           'consignments',  'change'),
('consignments.cod',              'Thanh toán COD',             'consignments',  'approve'),
-- Tuyến đường
('routes.view',                   'Xem tuyến đường',            'routes',        'view'),
('routes.add',                    'Thêm tuyến đường',           'routes',        'add'),
('routes.change',                 'Sửa tuyến đường',            'routes',        'change'),
-- Nhân sự
('employees.view',                'Xem nhân sự',                'hr',            'view'),
('employees.add',                 'Thêm nhân sự',               'hr',            'add'),
('employees.change',              'Sửa nhân sự',                'hr',            'change'),
('attendance.view',               'Xem chấm công',              'hr',            'view'),
('attendance.change',             'Sửa chấm công',              'hr',            'change'),
('payroll.view',                  'Xem bảng lương',             'hr',            'view'),
('payroll.approve',               'Duyệt lương',                'hr',            'approve'),
-- Tài chính
('expenses.view',                 'Xem chi phí',                'finance',       'view'),
('expenses.add',                  'Thêm chi phí',               'finance',       'add'),
('expenses.approve',              'Duyệt chi phí',              'finance',       'approve'),
('reports.view',                  'Xem báo cáo',                'finance',       'view'),
('reports.export',                'Xuất báo cáo',               'finance',       'export'),
-- Khách hàng
('customers.view',                'Xem khách hàng',             'customers',     'view'),
('customers.add',                 'Thêm khách hàng',            'customers',     'add'),
('customers.change',              'Sửa khách hàng',             'customers',     'change'),
-- Thanh toán
('payments.view',                 'Xem thanh toán',             'payments',      'view'),
('payments.refund',               'Hoàn tiền',                  'payments',      'approve'),
('invoices.view',                 'Xem hoá đơn',                'payments',      'view'),
('invoices.issue',                'Xuất hoá đơn',               'payments',      'add'),
('cashier_sessions.manage',       'Quản lý ca thu ngân',        'payments',      'change'),
-- Khuyến mãi
('promotions.view',               'Xem khuyến mãi',             'promotions',    'view'),
('promotions.add',                'Thêm khuyến mãi',            'promotions',    'add'),
('promotions.change',             'Sửa khuyến mãi',             'promotions',    'change'),
-- Admin
('users.view',                    'Xem tài khoản',              'accounts',      'view'),
('users.add',                     'Thêm tài khoản',             'accounts',      'add'),
('users.change',                  'Sửa tài khoản',              'accounts',      'change'),
('roles.view',                    'Xem vai trò',                'accounts',      'view'),
('roles.change',                  'Sửa phân quyền',             'accounts',      'change'),
('audit_logs.view',               'Xem audit log',              'accounts',      'view'),
('system_config.view',            'Xem cấu hình hệ thống',      'settings',      'view'),
('system_config.change',          'Sửa cấu hình hệ thống',      'settings',      'change'),
('feature_flags.change',          'Bật/tắt tính năng',          'settings',      'change'),
('menus.change',                  'Quản lý menu',               'settings',      'change');

-- =============================================================================
-- SEED DATA: Default roles
-- =============================================================================

INSERT INTO roles (name, slug, description, is_system) VALUES
('Super Admin',   'super-admin',    'Toàn quyền hệ thống',         TRUE),
('Quản lý',       'manager',        'Quản lý chi nhánh',            TRUE),
('Thu ngân',      'cashier',        'Bán vé và thanh toán',         TRUE),
('Điều phối',     'dispatcher',     'Điều xe và lên lịch chuyến',   TRUE),
('Kế toán',       'accountant',     'Quản lý tài chính và báo cáo', TRUE),
('Nhân sự',       'hr-staff',       'Quản lý nhân sự và lương',     TRUE),
('Tài xế',        'driver',         'Tài xế xe',                    TRUE),
('Nhân viên kho', 'cargo-staff',    'Quản lý hàng hoá',             TRUE),
('Chỉ xem',       'viewer',         'Quyền đọc toàn bộ module',     FALSE);

-- =============================================================================
-- SEED DATA: Menu groups & items (mapping với sidebar.html)
-- =============================================================================

INSERT INTO menu_groups (code, label, sort_order) VALUES
('dashboard',    'Tổng quan',      0),
('operations',   'Vận hành xe',    1),
('cargo',        'Hàng hoá',       2),
('routes',       'Hành trình',     3),
('hr',           'Nhân sự',        4),
('finance',      'Tài chính',      5),
('customers',    'Khách hàng',     6),
('marketing',    'Khuyến mãi',     7),
('admin',        'Quản trị',       8),
('settings',     'Cài đặt',        9);

-- Dashboard
INSERT INTO menu_items (group_id, code, label, url_path, permission_code, sort_order)
SELECT g.id, 'dashboard', 'Bảng điều khiển', '/dashboard/', 'dashboard.view', 0
FROM menu_groups g WHERE g.code = 'dashboard';

-- Vận hành xe
INSERT INTO menu_items (group_id, code, label, url_path, permission_code, sort_order)
SELECT g.id, v.code, v.label, v.url, v.perm, v.ord
FROM menu_groups g, (VALUES
    ('ticket-quick-book', 'Đặt vé nhanh',          '/tickets/quick-book/',    'tickets.add',       1),
    ('ticket-bookings',   'Danh sách phiếu đặt',   '/tickets/bookings/',      'bookings.view',     2),
    ('ticket-lookup',     'Tra cứu vé',             '/tickets/lookup/',        'tickets.view',      3),
    ('trip-schedules',    'Tạo/quản lý lịch chuyến','/trips/schedules/',      'trips.add',         4),
    ('trip-prices',       'Giá vé theo chuyến/ghế', '/trips/prices/',         'trip_prices.view',  5),
    ('trip-status',       'Trạng thái chuyến',      '/trips/status/',          'trips.view',        6),
    ('ticket-refund',     'Hoàn & Đổi vé',          '/tickets/refunds/',       'bookings.refund',   7),
    ('group-contracts',   'Bán vé nhóm/hợp đồng',  '/tickets/group/',         'bookings.view',     8),
    ('vehicles-list',     'Danh sách xe',           '/vehicles/',              'vehicles.view',     9),
    ('vehicles-maintenance','Bảo dưỡng xe',         '/vehicles/maintenance/',  'vehicles.maintenance',10),
    ('dispatch',          'Điều phối xe',           '/trips/dispatch/',        'trips.dispatch',    11)
) AS v(code, label, url, perm, ord)
WHERE g.code = 'operations';

-- Hàng hoá
INSERT INTO menu_items (group_id, code, label, url_path, permission_code, sort_order)
SELECT g.id, v.code, v.label, v.url, v.perm, v.ord
FROM menu_groups g, (VALUES
    ('consignment-new',      'Tạo vận đơn mới',          '/cargo/new/',              'consignments.add',    1),
    ('consignment-list',     'Danh sách vận đơn',        '/cargo/',                  'consignments.view',   2),
    ('consignment-tracking', 'Theo dõi hàng hoá',        '/cargo/tracking/',         'consignments.view',   3),
    ('cargo-manifest',       'Bảng kê hàng chuyến',      '/cargo/manifest/',         'consignments.view',   4),
    ('cod-management',       'Quản lý COD',              '/cargo/cod/',              'consignments.cod',    5),
    ('cargo-pricing',        'Bảng giá cước hàng hoá',   '/cargo/pricing/',          'consignments.view',   6)
) AS v(code, label, url, perm, ord)
WHERE g.code = 'cargo';

-- Hành trình
INSERT INTO menu_items (group_id, code, label, url_path, permission_code, sort_order)
SELECT g.id, v.code, v.label, v.url, v.perm, v.ord
FROM menu_groups g, (VALUES
    ('routes-list',  'Danh sách tuyến đường', '/routes/',          'routes.view',  1),
    ('routes-add',   'Thêm tuyến đường mới',  '/routes/add/',      'routes.add',   2),
    ('stations',     'Điểm dừng / trạm',      '/routes/stations/', 'routes.view',  3)
) AS v(code, label, url, perm, ord)
WHERE g.code = 'routes';

-- Nhân sự
INSERT INTO menu_items (group_id, code, label, url_path, permission_code, sort_order)
SELECT g.id, v.code, v.label, v.url, v.perm, v.ord
FROM menu_groups g, (VALUES
    ('employees-list',  'Danh sách nhân sự',  '/hr/employees/',   'employees.view',    1),
    ('employees-add',   'Thêm nhân sự mới',   '/hr/employees/add/','employees.add',    2),
    ('attendance',      'Chấm công',           '/hr/attendance/',  'attendance.view',   3),
    ('leave-requests',  'Quản lý nghỉ phép',   '/hr/leaves/',      'attendance.view',   4),
    ('payroll',         'Bảng lương',          '/hr/payroll/',     'payroll.view',      5)
) AS v(code, label, url, perm, ord)
WHERE g.code = 'hr';

-- Tài chính
INSERT INTO menu_items (group_id, code, label, url_path, permission_code, sort_order)
SELECT g.id, v.code, v.label, v.url, v.perm, v.ord
FROM menu_groups g, (VALUES
    ('cashier-session','Ca thu ngân',              '/finance/cashier/',    'cashier_sessions.manage', 1),
    ('invoices',       'Hoá đơn điện tử',          '/finance/invoices/',   'invoices.view',          2),
    ('expenses',       'Chi phí vận hành',         '/finance/expenses/',   'expenses.view',          3),
    ('fuel',           'Cấp nhiên liệu',           '/finance/fuel/',       'expenses.view',          4),
    ('reports-revenue','Báo cáo doanh thu',        '/reports/revenue/',    'reports.view',           5),
    ('reports-ops',    'Báo cáo vận hành',         '/reports/operations/', 'reports.view',           6)
) AS v(code, label, url, perm, ord)
WHERE g.code = 'finance';

-- Khách hàng
INSERT INTO menu_items (group_id, code, label, url_path, permission_code, sort_order)
SELECT g.id, v.code, v.label, v.url, v.perm, v.ord
FROM menu_groups g, (VALUES
    ('customers-list','Danh sách khách hàng', '/customers/',      'customers.view', 1),
    ('customers-add', 'Thêm khách hàng',      '/customers/add/',  'customers.add',  2),
    ('loyalty',       'Điểm tích lũy',        '/customers/loyalty/','customers.view',3)
) AS v(code, label, url, perm, ord)
WHERE g.code = 'customers';

-- Khuyến mãi
INSERT INTO menu_items (group_id, code, label, url_path, permission_code, sort_order)
SELECT g.id, v.code, v.label, v.url, v.perm, v.ord
FROM menu_groups g, (VALUES
    ('promotions-list', 'Danh sách khuyến mãi', '/marketing/promotions/', 'promotions.view', 1),
    ('promotions-add',  'Thêm khuyến mãi',      '/marketing/promotions/add/','promotions.add',2),
    ('after-sales',     'Chăm sóc sau bán',     '/marketing/after-sales/', 'promotions.view', 3)
) AS v(code, label, url, perm, ord)
WHERE g.code = 'marketing';

-- Quản trị
INSERT INTO menu_items (group_id, code, label, url_path, permission_code, sort_order)
SELECT g.id, v.code, v.label, v.url, v.perm, v.ord
FROM menu_groups g, (VALUES
    ('users-list',    'Danh sách tài khoản', '/admin/users/',       'users.view',     1),
    ('users-add',     'Thêm tài khoản mới',  '/admin/users/add/',   'users.add',      2),
    ('roles-list',    'Danh sách vai trò',   '/admin/roles/',       'roles.view',     3),
    ('permissions',   'Danh sách quyền',     '/admin/permissions/', 'roles.view',     4),
    ('assign-perm',   'Gán quyền',           '/admin/roles/assign-perm/','roles.change',5),
    ('assign-role',   'Gán vai trò',         '/admin/users/assign-role/','roles.change',6),
    ('audit-logs',    'Lịch sử thao tác',    '/admin/audit-logs/',  'audit_logs.view',7),
    ('branches',      'Quản lý chi nhánh',   '/admin/branches/',    'users.view',     8),
    ('api-tokens',    'Quản lý API Token',   '/admin/api-tokens/',  'system_config.change',9)
) AS v(code, label, url, perm, ord)
WHERE g.code = 'admin';

-- Cài đặt
INSERT INTO menu_items (group_id, code, label, url_path, permission_code, sort_order)
SELECT g.id, v.code, v.label, v.url, v.perm, v.ord
FROM menu_groups g, (VALUES
    ('system-config',  'Cấu hình hệ thống',  '/settings/config/',  'system_config.change', 1),
    ('feature-flags',  'Bật/tắt tính năng',  '/settings/features/','feature_flags.change', 2),
    ('menu-editor',    'Quản lý menu',        '/settings/menus/',   'menus.change',         3),
    ('notification-tpl','Mẫu thông báo',     '/settings/notif-templates/','system_config.view',4),
    ('webhooks',       'Webhook',             '/settings/webhooks/', 'system_config.change', 5),
    ('report-builder', 'Thiết kế báo cáo',   '/settings/reports/', 'reports.export',        6)
) AS v(code, label, url, perm, ord)
WHERE g.code = 'settings';

-- =============================================================================
-- COMMENTS: Architecture notes
-- =============================================================================
COMMENT ON TABLE tenants            IS 'Multi-tenant foundation. Single-tenant: always tenant_id=1.';
COMMENT ON TABLE menu_items         IS 'DB-driven sidebar navigation. Linked to permissions for RBAC.';
COMMENT ON TABLE system_configs     IS 'Runtime config store. Changes logged in system_config_history.';
COMMENT ON TABLE feature_flags      IS 'Feature toggle per tenant/role/user for safe rollout.';
COMMENT ON TABLE api_tokens         IS 'API key management. Raw token never stored, only sha256 hash.';
COMMENT ON TABLE trip_tracking      IS 'Partitioned by year. Add new partition yearly via ALTER TABLE.';
COMMENT ON TABLE audit_logs         IS 'Partitioned by year. Add new partition yearly via ALTER TABLE.';
COMMENT ON TABLE notifications      IS 'Partitioned by year. Add new partition yearly via ALTER TABLE.';
COMMENT ON TABLE consignment_events IS 'Full history trail for each consignment status change.';
COMMENT ON TABLE webhook_deliveries IS 'Delivery log with retry support for outbound integrations.';

-- END OF SCHEMA