from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = '1234'


# Function to get SQLite database connection
def get_db_connection():
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print("Database connection error:", e)
        return None



@app.route('/admin_reports', methods=['GET'])
def admin_reports():
    if 'role' in session and session['role'] == 'admin':
        # Fetch the necessary data from the database for reporting
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT status, COUNT(*) AS total_tickets FROM tickets GROUP BY status")
        ticket_report = cursor.fetchall()

        cursor.execute("SELECT AVG(rating) AS avg_rating FROM feedback GROUP BY ticket_id")
        feedback_report = cursor.fetchall()

        cursor.execute("SELECT status, COUNT(*) AS total_requests FROM support_requests GROUP BY status")
        support_report = cursor.fetchall()

        conn.close()  # Close the database connection

        return render_template('admin_reports.html',
                               ticket_report=ticket_report,
                               feedback_report=feedback_report,
                               support_report=support_report)
    else:
        return redirect(url_for('login'))  # Redirect if not logged in as admin


@app.route('/view_feedbacks', methods=['GET'])
def view_feedbacks():
    if 'role' in session and session['role'] == 'admin':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM feedbacks")
        feedbacks = cursor.fetchall()
        conn.close()  # Close the database connection
        return render_template('view_feedbacks.html', feedbacks=feedbacks)
    else:
        return redirect(url_for('login'))  # Redirect if not logged in as admin


@app.route('/view_support_requests', methods=['GET'])
def view_support_requests():
    if 'role' in session and session['role'] == 'admin':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM support_requests")
        support_requests = cursor.fetchall()
        conn.close()  # Close the database connection
        return render_template('view_support_requests.html', support_requests=support_requests)
    else:
        return redirect(url_for('login'))  # Redirect if not logged in as admin
