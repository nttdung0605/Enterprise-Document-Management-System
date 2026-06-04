-- Departments
INSERT INTO departments (
    name,
    quota_max
)
VALUES
('IT', 1073741824),
('HR', 536870912),
('Finance', 536870912);

-- Users
INSERT INTO users (
    username,
    password_hash,
    role,
    department_id,
    personal_quota_max
)
VALUES
(
    'admin',
    '123456',
    'admin',
    1,
    536870912
),
(
    'manager_it',
    '123456',
    'manager',
    1,
    268435456
),
(
    'staff_it',
    '123456',
    'staff',
    1,
    134217728
),
(
    'staff_hr',
    '123456',
    'staff',
    2,
    134217728
);

UPDATE users
SET
personal_quota_max = 1000
WHERE username='staff_it';