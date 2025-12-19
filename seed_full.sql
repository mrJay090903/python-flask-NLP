-- Create database
CREATE DATABASE IF NOT EXISTS py_data_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE py_data_app;

-- Roles
CREATE TABLE IF NOT EXISTS roles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL
);

-- Users
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(80) UNIQUE NOT NULL,
  email VARCHAR(120) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role_id INT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL
);

-- Navigation
CREATE TABLE IF NOT EXISTS nav_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(120) NOT NULL,
  endpoint VARCHAR(255) NOT NULL,
  position INT DEFAULT 0,
  roles_allowed VARCHAR(255),
  visible TINYINT(1) DEFAULT 1
);

-- Records
CREATE TABLE IF NOT EXISTS records (
  id INT AUTO_INCREMENT PRIMARY KEY,
  category VARCHAR(100) NOT NULL,
  subcategory VARCHAR(100),
  value FLOAT NOT NULL,
  recorded_at DATETIME NOT NULL,
  created_by INT,
  KEY idx_category (category),
  KEY idx_recorded_at (recorded_at),
  KEY idx_category_date (category, recorded_at),
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Insert default roles
INSERT IGNORE INTO roles (name) VALUES 
('Admin'),
('President'),
('Cashier'),
('Viewer');

-- Insert a default admin user (password=admin, will be hashed by app)
INSERT IGNORE INTO users (username, email, password_hash, role_id)
VALUES ('admin', 'admin@example.com', 'pbkdf2:sha256:600000$H9U8pJ0q$8d8c6b3e5c7a9b1d3f5e7a9b1d3f5e7a9b1d3f5e', 
  (SELECT id FROM roles WHERE name='Admin'));

-- Insert navigation items
INSERT IGNORE INTO nav_items (title, endpoint, position, roles_allowed, visible) VALUES
('Home', 'index', 1, 'Admin,President,Cashier,Viewer', 1),
('Records', 'records.list_records', 2, 'Admin,President,Cashier,Viewer', 1),
('Charts', 'charts', 3, 'Admin,President,Viewer', 1),
('Admin - Users', 'admin.list_users', 100, 'Admin', 1),
('Admin - Navigation', 'admin.list_nav', 101, 'Admin', 1);

-- Insert sample records
INSERT INTO records (category, subcategory, value, recorded_at) VALUES
('Sales', 'Online', 120.50, '2025-01-01 10:00:00'),
('Sales', 'Offline', 200.00, '2025-01-02 11:00:00'),
('Sales', 'Online', 90.25, '2025-01-03 09:30:00'),
('Support', 'Email', 50.00, '2025-01-01 12:00:00'),
('Support', 'Phone', 70.00, '2025-01-04 14:00:00'),
('Expenses', 'Utilities', -150.00, '2025-01-05 15:00:00'),
('Expenses', 'Supplies', -75.50, '2025-01-06 16:00:00');

-- Create index for users
CREATE INDEX idx_username ON users(username);
CREATE INDEX idx_email ON users(email);

COMMIT;
