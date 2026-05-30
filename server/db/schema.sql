-- Kích hoạt kiểm tra khóa ngoại trong SQLite
PRAGMA foreign_keys = ON;

-- 1. Bảng Phòng ban
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,       -- Tên phòng ban (HR, Finance, IT, Sales)
    quota_max BIGINT NOT NULL,              -- Tổng dung lượng phòng ban cho phép (bytes)
    quota_used BIGINT DEFAULT 0             -- Dung lượng phòng ban đang sử dụng (bytes)
);

-- 2. Bảng Người dùng
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,              -- 'admin', 'manager', 'staff'
    department_id INTEGER NOT NULL,
    personal_quota_max BIGINT NOT NULL,     -- Dung lượng cá nhân tối đa (bytes)
    personal_quota_used BIGINT DEFAULT 0,   -- Dung lượng cá nhân đang sử dụng (bytes)
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- 3. Bảng Tài liệu chung (Gom nhóm version)
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255) NOT NULL,
    department_id INTEGER NOT NULL,
    UNIQUE(filename, department_id),        -- Đảm bảo tên file duy nhất trong một phòng ban
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- 4. Bảng Phiên bản tài liệu
CREATE TABLE IF NOT EXISTS document_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    version_num INTEGER NOT NULL,           -- Số thứ tự version (1, 2, 3...)
    uploaded_by INTEGER NOT NULL,           -- User ID của người upload
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',   -- 'pending', 'approved', 'rejected'
    filepath VARCHAR(255) NOT NULL,         -- Đường dẫn lưu file mã hóa trên ổ cứng server
    filesize BIGINT NOT NULL,               -- Kích thước file (bytes)
    checksum VARCHAR(64) NOT NULL,          -- Chuỗi SHA256
    FOREIGN KEY (document_id) REFERENCES documents(id),
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

-- 5. Bảng Audit Log
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action VARCHAR(50) NOT NULL,            -- 'UPLOAD', 'APPROVE', 'REJECT', 'DOWNLOAD'
    user_id INTEGER NOT NULL,               -- User thực hiện hành động
    version_id INTEGER NOT NULL,            -- Version bị tác động
    action_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    client_ip VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (version_id) REFERENCES document_versions(id)
);

-- Tạo Index để tăng tốc độ truy vấn cho các nghiệp vụ tìm kiếm thường xuyên
CREATE INDEX idx_docs_department ON documents(department_id);
CREATE INDEX idx_versions_status ON document_versions(status);
CREATE INDEX idx_audit_user ON audit_logs(user_id);