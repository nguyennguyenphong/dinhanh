-- =============================================================================
-- Bus CMS - PostgreSQL Schema
-- Generated for production use
-- =============================================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =============================================================================
-- APP: accounts
-- =============================================================================

CREATE TABLE roles (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE permissions (
    id          SERIAL PRIMARY KEY,
    codename    VARCHAR(150) NOT NULL UNIQUE,   -- e.g. "tickets.add_ticket"
    name        VARCHAR(255) NOT NULL,
    module      VARCHAR(100) NOT NULL,           -- e.g. "tickets", "vehicles"
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE role_permissions (
    role_id       INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE user_accounts (
    id            SERIAL PRIMARY KEY,
    uuid          UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    username      VARCHAR(150) NOT NULL UNIQUE,
    email         VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(255) NOT NULL,
    phone         VARCHAR(20),
    avatar        VARCHAR(500),
    branch_id     INTEGER,                       -- FK added after branches table
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    is_staff      BOOLEAN NOT NULL DEFAULT FALSE,
    is_superuser  BOOLEAN NOT NULL DEFAULT FALSE,
    last_login    TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_roles (
    user_id INTEGER NOT NULL REFERENCES user_accounts(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE audit_logs (
    id          BIGSERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    username    VARCHAR(150),                    -- snapshot at time of action
    action      VARCHAR(50) NOT NULL,            -- CREATE, UPDATE, DELETE, LOGIN, etc.
    module      VARCHAR(100) NOT NULL,
    object_id   VARCHAR(50),
    object_repr VARCHAR(500),
    changes     JSONB,
    ip_address  INET,
    user_agent  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- APP: branches
-- =============================================================================

CREATE TABLE branches (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(20) NOT NULL UNIQUE,
    name        VARCHAR(255) NOT NULL,
    address     TEXT,
    phone       VARCHAR(20),
    email       VARCHAR(254),
    manager_id  INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add deferred FK: user_accounts.branch_id -> branches.id
ALTER TABLE user_accounts
    ADD CONSTRAINT fk_user_branch FOREIGN KEY (branch_id)
    REFERENCES branches(id) ON DELETE SET NULL;

-- =============================================================================
-- APP: routes
-- =============================================================================

CREATE TABLE provinces (
    id        SERIAL PRIMARY KEY,
    code      VARCHAR(10) NOT NULL UNIQUE,
    name      VARCHAR(100) NOT NULL
);

CREATE TABLE stations (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(20) NOT NULL UNIQUE,
    name        VARCHAR(255) NOT NULL,
    province_id INTEGER NOT NULL REFERENCES provinces(id),
    address     TEXT,
    latitude    NUMERIC(10, 7),
    longitude   NUMERIC(10, 7),
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE routes (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(20) NOT NULL UNIQUE,
    name            VARCHAR(255) NOT NULL,
    origin_id       INTEGER NOT NULL REFERENCES stations(id),
    destination_id  INTEGER NOT NULL REFERENCES stations(id),
    distance_km     NUMERIC(8, 2),
    duration_min    INTEGER,                     -- estimated travel time in minutes
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE route_stops (
    id          SERIAL PRIMARY KEY,
    route_id    INTEGER NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    station_id  INTEGER NOT NULL REFERENCES stations(id),
    stop_order  SMALLINT NOT NULL,
    arrive_offset_min INTEGER,                   -- minutes from departure
    depart_offset_min INTEGER,
    UNIQUE (route_id, stop_order)
);

-- =============================================================================
-- APP: vehicles
-- =============================================================================

CREATE TABLE vehicle_categories (
    id            SERIAL PRIMARY KEY,
    code          VARCHAR(20) NOT NULL UNIQUE,
    name          VARCHAR(100) NOT NULL,         -- e.g. "Giường nằm 40 chỗ"
    seat_count    SMALLINT NOT NULL,
    vehicle_type  VARCHAR(50) NOT NULL,          -- BUS, SLEEPER_BUS, LIMOUSINE
    description   TEXT,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE vehicles (
    id              SERIAL PRIMARY KEY,
    plate_number    VARCHAR(20) NOT NULL UNIQUE,
    category_id     INTEGER NOT NULL REFERENCES vehicle_categories(id),
    branch_id       INTEGER REFERENCES branches(id) ON DELETE SET NULL,
    manufacture_year SMALLINT,
    brand           VARCHAR(100),
    model           VARCHAR(100),
    color           VARCHAR(50),
    status          VARCHAR(30) NOT NULL DEFAULT 'AVAILABLE',
    -- AVAILABLE, IN_TRIP, MAINTENANCE, INACTIVE
    registration_expiry DATE,
    insurance_expiry    DATE,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE seat_maps (
    id              SERIAL PRIMARY KEY,
    category_id     INTEGER NOT NULL REFERENCES vehicle_categories(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,       -- e.g. "Tầng 1 - Hàng A"
    total_seats     SMALLINT NOT NULL,
    layout_config   JSONB NOT NULL DEFAULT '{}', -- rows/cols/deck config
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE seats (
    id           SERIAL PRIMARY KEY,
    seat_map_id  INTEGER NOT NULL REFERENCES seat_maps(id) ON DELETE CASCADE,
    seat_code    VARCHAR(10) NOT NULL,           -- e.g. "A1", "B2"
    seat_type    VARCHAR(30) NOT NULL DEFAULT 'SEAT',  -- SEAT, BED, VIP
    deck         SMALLINT NOT NULL DEFAULT 1,
    row_num      SMALLINT,
    col_num      SMALLINT,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (seat_map_id, seat_code)
);

CREATE TABLE vehicle_maintenance (
    id           SERIAL PRIMARY KEY,
    vehicle_id   INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    type         VARCHAR(30) NOT NULL,           -- SCHEDULED, EMERGENCY
    description  TEXT NOT NULL,
    cost         NUMERIC(15, 2),
    vendor       VARCHAR(255),
    scheduled_at DATE,
    completed_at DATE,
    performed_by INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    status       VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING, DONE
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- APP: hr (human resources)
-- =============================================================================

CREATE TABLE departments (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE employees (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(20) NOT NULL UNIQUE,
    full_name       VARCHAR(255) NOT NULL,
    national_id     VARCHAR(20),
    phone           VARCHAR(20),
    email           VARCHAR(254),
    date_of_birth   DATE,
    gender          VARCHAR(10),                 -- MALE, FEMALE, OTHER
    address         TEXT,
    position        VARCHAR(100) NOT NULL,       -- DRIVER, ASSISTANT, CASHIER, etc.
    department_id   INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    branch_id       INTEGER REFERENCES branches(id) ON DELETE SET NULL,
    user_account_id INTEGER UNIQUE REFERENCES user_accounts(id) ON DELETE SET NULL,
    hired_at        DATE NOT NULL,
    terminated_at   DATE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    -- Driver-specific fields
    license_number  VARCHAR(50),
    license_class   VARCHAR(10),
    license_expiry  DATE,
    -- Insurance
    social_insurance_no VARCHAR(20),
    health_insurance_no VARCHAR(20),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE shift_types (
    id         SERIAL PRIMARY KEY,
    code       VARCHAR(20) NOT NULL UNIQUE,
    name       VARCHAR(100) NOT NULL,
    start_time TIME NOT NULL,
    end_time   TIME NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE attendances (
    id             SERIAL PRIMARY KEY,
    employee_id    INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    shift_type_id  INTEGER REFERENCES shift_types(id) ON DELETE SET NULL,
    work_date      DATE NOT NULL,
    check_in       TIMESTAMPTZ,
    check_out      TIMESTAMPTZ,
    status         VARCHAR(20) NOT NULL DEFAULT 'PRESENT',
    -- PRESENT, ABSENT, LATE, HALF_DAY, LEAVE
    notes          TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (employee_id, work_date)
);

CREATE TABLE payroll (
    id              SERIAL PRIMARY KEY,
    employee_id     INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    period_year     SMALLINT NOT NULL,
    period_month    SMALLINT NOT NULL,
    base_salary     NUMERIC(15, 2) NOT NULL DEFAULT 0,
    allowances      NUMERIC(15, 2) NOT NULL DEFAULT 0,
    deductions      NUMERIC(15, 2) NOT NULL DEFAULT 0,
    bonus           NUMERIC(15, 2) NOT NULL DEFAULT 0,
    net_salary      NUMERIC(15, 2) NOT NULL DEFAULT 0,
    status          VARCHAR(20) NOT NULL DEFAULT 'DRAFT', -- DRAFT, APPROVED, PAID
    approved_by     INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    paid_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (employee_id, period_year, period_month)
);

-- =============================================================================
-- APP: trips (schedule + dispatch)
-- =============================================================================

CREATE TABLE trip_schedules (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(30) NOT NULL UNIQUE,
    route_id        INTEGER NOT NULL REFERENCES routes(id),
    departure_time  TIME NOT NULL,
    arrival_time    TIME,
    days_of_week    SMALLINT[] NOT NULL DEFAULT '{1,2,3,4,5,6,7}',
    -- 1=Mon ... 7=Sun
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE trips (
    id                  SERIAL PRIMARY KEY,
    code                VARCHAR(30) NOT NULL UNIQUE,
    schedule_id         INTEGER REFERENCES trip_schedules(id) ON DELETE SET NULL,
    route_id            INTEGER NOT NULL REFERENCES routes(id),
    vehicle_id          INTEGER REFERENCES vehicles(id) ON DELETE SET NULL,
    seat_map_id         INTEGER REFERENCES seat_maps(id) ON DELETE SET NULL,
    departure_time      TIMESTAMPTZ NOT NULL,
    estimated_arrival   TIMESTAMPTZ,
    actual_departure    TIMESTAMPTZ,
    actual_arrival      TIMESTAMPTZ,
    status              VARCHAR(30) NOT NULL DEFAULT 'SCHEDULED',
    -- SCHEDULED, BOARDING, DEPARTED, ARRIVED, CANCELLED, DELAYED
    branch_id           INTEGER REFERENCES branches(id) ON DELETE SET NULL,
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE trip_staff (
    id          SERIAL PRIMARY KEY,
    trip_id     INTEGER NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    role        VARCHAR(30) NOT NULL,            -- DRIVER, ASSISTANT
    shift_type_id INTEGER REFERENCES shift_types(id) ON DELETE SET NULL,
    UNIQUE (trip_id, employee_id)
);

CREATE TABLE trip_prices (
    id          SERIAL PRIMARY KEY,
    route_id    INTEGER NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    seat_type   VARCHAR(30) NOT NULL DEFAULT 'SEAT',
    price       NUMERIC(15, 2) NOT NULL,
    valid_from  DATE NOT NULL,
    valid_to    DATE,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE dispatch_orders (
    id              SERIAL PRIMARY KEY,
    trip_id         INTEGER NOT NULL UNIQUE REFERENCES trips(id),
    issued_by       INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    issued_at       TIMESTAMPTZ,
    notes           TEXT,
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    -- PENDING, ISSUED, DEPARTED
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- APP: tickets
-- =============================================================================

CREATE TABLE customers (
    id         SERIAL PRIMARY KEY,
    full_name  VARCHAR(255) NOT NULL,
    phone      VARCHAR(20) NOT NULL,
    email      VARCHAR(254),
    national_id VARCHAR(20),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_customers_phone ON customers(phone);

CREATE TABLE ticket_bookings (
    id              BIGSERIAL PRIMARY KEY,
    booking_code    VARCHAR(30) NOT NULL UNIQUE,
    customer_id     INTEGER NOT NULL REFERENCES customers(id),
    trip_id         INTEGER NOT NULL REFERENCES trips(id),
    booked_by       INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    channel         VARCHAR(30) NOT NULL DEFAULT 'COUNTER',
    -- COUNTER, ONLINE, AGENT
    status          VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    -- PENDING, CONFIRMED, CANCELLED, REFUNDED
    total_amount    NUMERIC(15, 2) NOT NULL DEFAULT 0,
    discount_amount NUMERIC(15, 2) NOT NULL DEFAULT 0,
    final_amount    NUMERIC(15, 2) NOT NULL DEFAULT 0,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tickets (
    id              BIGSERIAL PRIMARY KEY,
    ticket_code     VARCHAR(30) NOT NULL UNIQUE,
    booking_id      BIGINT NOT NULL REFERENCES ticket_bookings(id) ON DELETE CASCADE,
    seat_id         INTEGER REFERENCES seats(id) ON DELETE SET NULL,
    seat_code       VARCHAR(10),                 -- snapshot
    seat_type       VARCHAR(30) NOT NULL DEFAULT 'SEAT',
    boarding_station_id  INTEGER REFERENCES stations(id) ON DELETE SET NULL,
    alighting_station_id INTEGER REFERENCES stations(id) ON DELETE SET NULL,
    passenger_name  VARCHAR(255),
    passenger_phone VARCHAR(20),
    base_price      NUMERIC(15, 2) NOT NULL,
    discount_amount NUMERIC(15, 2) NOT NULL DEFAULT 0,
    final_price     NUMERIC(15, 2) NOT NULL,
    status          VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    -- ACTIVE, USED, CANCELLED, REFUNDED, EXCHANGED
    checked_in_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ticket_refunds (
    id              BIGSERIAL PRIMARY KEY,
    ticket_id       BIGINT NOT NULL REFERENCES tickets(id),
    refund_code     VARCHAR(30) NOT NULL UNIQUE,
    reason          TEXT,
    original_amount NUMERIC(15, 2) NOT NULL,
    penalty_amount  NUMERIC(15, 2) NOT NULL DEFAULT 0,
    refund_amount   NUMERIC(15, 2) NOT NULL,
    refund_method   VARCHAR(30),                 -- CASH, BANK_TRANSFER, WALLET
    processed_by    INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    -- PENDING, APPROVED, COMPLETED, REJECTED
    processed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ticket_exchanges (
    id              BIGSERIAL PRIMARY KEY,
    original_ticket_id BIGINT NOT NULL REFERENCES tickets(id),
    new_ticket_id   BIGINT REFERENCES tickets(id) ON DELETE SET NULL,
    exchange_code   VARCHAR(30) NOT NULL UNIQUE,
    reason          TEXT,
    fee             NUMERIC(15, 2) NOT NULL DEFAULT 0,
    processed_by    INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Group / contract bookings
CREATE TABLE group_contracts (
    id              SERIAL PRIMARY KEY,
    contract_code   VARCHAR(30) NOT NULL UNIQUE,
    customer_name   VARCHAR(255) NOT NULL,
    customer_phone  VARCHAR(20) NOT NULL,
    customer_email  VARCHAR(254),
    trip_id         INTEGER NOT NULL REFERENCES trips(id),
    seat_count      SMALLINT NOT NULL,
    total_amount    NUMERIC(15, 2) NOT NULL,
    deposit_amount  NUMERIC(15, 2) NOT NULL DEFAULT 0,
    status          VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
    -- DRAFT, CONFIRMED, CANCELLED, COMPLETED
    contract_file   VARCHAR(500),
    notes           TEXT,
    created_by      INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- APP: payments
-- =============================================================================

CREATE TABLE payment_methods (
    id         SERIAL PRIMARY KEY,
    code       VARCHAR(30) NOT NULL UNIQUE,      -- CASH, CARD, MOMO, VNPAY, etc.
    name       VARCHAR(100) NOT NULL,
    is_active  BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE payments (
    id              BIGSERIAL PRIMARY KEY,
    payment_code    VARCHAR(30) NOT NULL UNIQUE,
    booking_id      BIGINT REFERENCES ticket_bookings(id) ON DELETE SET NULL,
    consignment_id  BIGINT,                      -- FK added after consignments table
    amount          NUMERIC(15, 2) NOT NULL,
    method_id       INTEGER NOT NULL REFERENCES payment_methods(id),
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    -- PENDING, SUCCESS, FAILED, REFUNDED
    transaction_ref VARCHAR(100),
    cashier_id      INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    branch_id       INTEGER REFERENCES branches(id) ON DELETE SET NULL,
    paid_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE cashier_sessions (
    id           SERIAL PRIMARY KEY,
    cashier_id   INTEGER NOT NULL REFERENCES user_accounts(id),
    branch_id    INTEGER NOT NULL REFERENCES branches(id),
    opened_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at    TIMESTAMPTZ,
    opening_cash NUMERIC(15, 2) NOT NULL DEFAULT 0,
    closing_cash NUMERIC(15, 2),
    total_sales  NUMERIC(15, 2),
    status       VARCHAR(20) NOT NULL DEFAULT 'OPEN',  -- OPEN, CLOSED
    notes        TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE invoices (
    id              SERIAL PRIMARY KEY,
    invoice_no      VARCHAR(50) NOT NULL UNIQUE,
    series          VARCHAR(10) NOT NULL,
    booking_id      BIGINT REFERENCES ticket_bookings(id) ON DELETE SET NULL,
    group_contract_id INTEGER REFERENCES group_contracts(id) ON DELETE SET NULL,
    buyer_name      VARCHAR(255),
    buyer_tax_code  VARCHAR(20),
    buyer_address   TEXT,
    subtotal        NUMERIC(15, 2) NOT NULL,
    vat_rate        NUMERIC(5, 2) NOT NULL DEFAULT 10.00,
    vat_amount      NUMERIC(15, 2) NOT NULL,
    total_amount    NUMERIC(15, 2) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
    -- DRAFT, ISSUED, CANCELLED
    e_invoice_code  VARCHAR(100),                -- from tax authority
    issued_at       TIMESTAMPTZ,
    issued_by       INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- APP: consignments (cargo)
-- =============================================================================

CREATE TABLE cargo_price_tables (
    id           SERIAL PRIMARY KEY,
    route_id     INTEGER REFERENCES routes(id) ON DELETE SET NULL,
    cargo_type   VARCHAR(50),                    -- NORMAL, FRAGILE, LIQUID, etc.
    min_weight   NUMERIC(8, 2),
    max_weight   NUMERIC(8, 2),
    min_volume   NUMERIC(8, 3),
    max_volume   NUMERIC(8, 3),
    price        NUMERIC(15, 2) NOT NULL,
    price_unit   VARCHAR(20) NOT NULL DEFAULT 'PER_KG',  -- PER_KG, PER_TRIP, FLAT
    is_active    BOOLEAN NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE consignments (
    id              BIGSERIAL PRIMARY KEY,
    waybill_code    VARCHAR(30) NOT NULL UNIQUE,
    barcode         VARCHAR(100) UNIQUE,
    trip_id         INTEGER REFERENCES trips(id) ON DELETE SET NULL,
    sender_name     VARCHAR(255) NOT NULL,
    sender_phone    VARCHAR(20) NOT NULL,
    receiver_name   VARCHAR(255) NOT NULL,
    receiver_phone  VARCHAR(20) NOT NULL,
    origin_station_id      INTEGER REFERENCES stations(id) ON DELETE SET NULL,
    destination_station_id INTEGER REFERENCES stations(id) ON DELETE SET NULL,
    cargo_type      VARCHAR(50),
    description     TEXT,
    weight_kg       NUMERIC(8, 2),
    volume_m3       NUMERIC(8, 3),
    declared_value  NUMERIC(15, 2),
    freight_charge  NUMERIC(15, 2) NOT NULL DEFAULT 0,
    cod_amount      NUMERIC(15, 2) NOT NULL DEFAULT 0,  -- Cash on Delivery
    cod_collected   BOOLEAN NOT NULL DEFAULT FALSE,
    cod_transferred BOOLEAN NOT NULL DEFAULT FALSE,
    status          VARCHAR(30) NOT NULL DEFAULT 'RECEIVED',
    -- RECEIVED, LOADED, IN_TRANSIT, DELIVERED, RETURNED, LOST
    received_by     INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    delivered_by    INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    received_at     TIMESTAMPTZ,
    delivered_at    TIMESTAMPTZ,
    branch_id       INTEGER REFERENCES branches(id) ON DELETE SET NULL,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE consignment_manifests (
    id             SERIAL PRIMARY KEY,
    manifest_code  VARCHAR(30) NOT NULL UNIQUE,
    trip_id        INTEGER NOT NULL REFERENCES trips(id),
    created_by     INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    status         VARCHAR(20) NOT NULL DEFAULT 'OPEN',  -- OPEN, CLOSED
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE manifest_items (
    id             SERIAL PRIMARY KEY,
    manifest_id    INTEGER NOT NULL REFERENCES consignment_manifests(id) ON DELETE CASCADE,
    consignment_id BIGINT NOT NULL REFERENCES consignments(id),
    loaded_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (manifest_id, consignment_id)
);

CREATE TABLE cod_reconciliations (
    id              SERIAL PRIMARY KEY,
    consignment_id  BIGINT NOT NULL REFERENCES consignments(id),
    amount          NUMERIC(15, 2) NOT NULL,
    transferred_by  INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    transferred_at  TIMESTAMPTZ,
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add deferred FK: payments.consignment_id -> consignments.id
ALTER TABLE payments
    ADD CONSTRAINT fk_payment_consignment FOREIGN KEY (consignment_id)
    REFERENCES consignments(id) ON DELETE SET NULL;

-- =============================================================================
-- APP: promotions
-- =============================================================================

CREATE TABLE promotions (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(50) NOT NULL UNIQUE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    discount_type   VARCHAR(20) NOT NULL,        -- PERCENT, FIXED_AMOUNT
    discount_value  NUMERIC(10, 2) NOT NULL,
    min_order_amount NUMERIC(15, 2),
    max_discount    NUMERIC(15, 2),
    usage_limit     INTEGER,
    usage_count     INTEGER NOT NULL DEFAULT 0,
    applicable_routes INTEGER[],                 -- NULL = all routes
    applicable_seat_types VARCHAR(30)[],
    valid_from      TIMESTAMPTZ NOT NULL,
    valid_to        TIMESTAMPTZ,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_by      INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE promotion_usages (
    id            BIGSERIAL PRIMARY KEY,
    promotion_id  INTEGER NOT NULL REFERENCES promotions(id),
    booking_id    BIGINT NOT NULL REFERENCES ticket_bookings(id),
    discount_applied NUMERIC(15, 2) NOT NULL,
    used_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE after_sales (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(50) NOT NULL UNIQUE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    type            VARCHAR(30) NOT NULL,        -- VOUCHER, LOYALTY_POINTS, GIFT
    value           NUMERIC(10, 2),
    conditions      JSONB NOT NULL DEFAULT '{}',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_by      INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- APP: notifications
-- =============================================================================

CREATE TABLE notification_templates (
    id         SERIAL PRIMARY KEY,
    code       VARCHAR(50) NOT NULL UNIQUE,
    name       VARCHAR(255) NOT NULL,
    channel    VARCHAR(20) NOT NULL,             -- SMS, EMAIL, PUSH
    subject    VARCHAR(500),
    body       TEXT NOT NULL,
    is_active  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE notifications (
    id           BIGSERIAL PRIMARY KEY,
    template_id  INTEGER REFERENCES notification_templates(id) ON DELETE SET NULL,
    recipient_type VARCHAR(20) NOT NULL,         -- USER, CUSTOMER, EMPLOYEE
    recipient_id   INTEGER,
    recipient_phone VARCHAR(20),
    recipient_email VARCHAR(254),
    channel      VARCHAR(20) NOT NULL,
    subject      VARCHAR(500),
    body         TEXT NOT NULL,
    status       VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    -- PENDING, SENT, FAILED
    sent_at      TIMESTAMPTZ,
    error_msg    TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- APP: financials (costs + reporting)
-- =============================================================================

CREATE TABLE expense_categories (
    id         SERIAL PRIMARY KEY,
    code       VARCHAR(30) NOT NULL UNIQUE,
    name       VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE expenses (
    id              BIGSERIAL PRIMARY KEY,
    category_id     INTEGER NOT NULL REFERENCES expense_categories(id),
    vehicle_id      INTEGER REFERENCES vehicles(id) ON DELETE SET NULL,
    trip_id         INTEGER REFERENCES trips(id) ON DELETE SET NULL,
    branch_id       INTEGER REFERENCES branches(id) ON DELETE SET NULL,
    title           VARCHAR(255) NOT NULL,
    amount          NUMERIC(15, 2) NOT NULL,
    expense_date    DATE NOT NULL,
    description     TEXT,
    attachment      VARCHAR(500),
    submitted_by    INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    approved_by     INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    -- PENDING, APPROVED, REJECTED
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE fuel_allocations (
    id           SERIAL PRIMARY KEY,
    vehicle_id   INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    trip_id      INTEGER REFERENCES trips(id) ON DELETE SET NULL,
    liters       NUMERIC(8, 2) NOT NULL,
    price_per_liter NUMERIC(10, 2) NOT NULL,
    total_cost   NUMERIC(15, 2) NOT NULL,
    allocated_by INTEGER REFERENCES user_accounts(id) ON DELETE SET NULL,
    allocated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes        TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- APP: assets
-- =============================================================================

CREATE TABLE asset_categories (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE assets (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(30) NOT NULL UNIQUE,
    name            VARCHAR(255) NOT NULL,
    category_id     INTEGER REFERENCES asset_categories(id) ON DELETE SET NULL,
    branch_id       INTEGER REFERENCES branches(id) ON DELETE SET NULL,
    serial_number   VARCHAR(100),
    purchase_date   DATE,
    purchase_price  NUMERIC(15, 2),
    current_value   NUMERIC(15, 2),
    status          VARCHAR(30) NOT NULL DEFAULT 'IN_USE',
    -- IN_USE, MAINTENANCE, DISPOSED, LOST
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE storage_units (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(30) NOT NULL UNIQUE,
    name        VARCHAR(100) NOT NULL,
    branch_id   INTEGER REFERENCES branches(id) ON DELETE SET NULL,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX idx_trips_departure      ON trips(departure_time);
CREATE INDEX idx_trips_status         ON trips(status);
CREATE INDEX idx_trips_route          ON trips(route_id);
CREATE INDEX idx_tickets_booking      ON tickets(booking_id);
CREATE INDEX idx_tickets_status       ON tickets(status);
CREATE INDEX idx_bookings_trip        ON ticket_bookings(trip_id);
CREATE INDEX idx_bookings_customer    ON ticket_bookings(customer_id);
CREATE INDEX idx_consignments_status  ON consignments(status);
CREATE INDEX idx_consignments_trip    ON consignments(trip_id);
CREATE INDEX idx_payments_booking     ON payments(booking_id);
CREATE INDEX idx_audit_user           ON audit_logs(user_id);
CREATE INDEX idx_audit_created        ON audit_logs(created_at DESC);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_expenses_date        ON expenses(expense_date);