from werkzeug.security import generate_password_hash
import sqlite3

# Connect to the database
conn = sqlite3.connect('database.db')

# Hash the password
hashed_password = generate_password_hash('1234', method='pbkdf2:sha256')

try:
    # Check if the admin user already exists
    existing_admin = conn.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone()
    if existing_admin:
        # Update the password if the admin user exists
        conn.execute('UPDATE users SET password = ? WHERE username = ?', (hashed_password, 'admin'))
        print("Admin password updated successfully.")
    else:
        # Insert a new admin user if it doesn't exist
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', ('admin', hashed_password, 'Admin'))
        print("Admin user created successfully.")
    
    conn.commit()
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    conn.close()
