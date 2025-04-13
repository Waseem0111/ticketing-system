from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = '1234'  # Set your secret key here

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('database.db')  # Use your database file name here
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/submit_ticket', methods=['GET', 'POST'])
def submit_ticket():
    if 'role' in session and session['role'] == 'client':
        if request.method == 'POST':
            ticket_type = request.form['ticket_type']
            description = request.form['ticket_description']
            submission_channel = request.form['submission_channel']
            submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Connect to SQLite database
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert ticket into database
            query = '''INSERT INTO tickets (username, ticket_type, description, submission_channel, submission_time, status)
                       VALUES (?, ?, ?, ?, ?, ?)'''
            cursor.execute(query, (
                session['username'], ticket_type, description, submission_channel, submission_time, 'Pending'))
            conn.commit()

            cursor.close()
            conn.close()

            result = f"Ticket submitted successfully on {submission_time}. Your ticket type is {ticket_type}."
            return render_template('submit_ticket.html', result=result)

        return render_template('submit_ticket.html', result='')
    return redirect(url_for('home'))

@app.route('/view_ticket_history')
def view_ticket_history():
    if 'role' in session and session['role'] == 'client':
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query tickets for the current user
        query = 'SELECT * FROM tickets WHERE username = ?'
        cursor.execute(query, (session['username'],))
        tickets = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('ticket_history.html', tickets=tickets)
    return redirect(url_for('home'))

@app.route('/check_ticket_status', methods=['GET', 'POST'])
def check_ticket_status():
    if 'role' in session and session['role'] == 'client':
        if request.method == 'POST':
            ticket_id = request.form['ticket_id']
            conn = get_db_connection()
            cursor = conn.cursor()

            query = 'SELECT status FROM tickets WHERE id = ? AND username = ?'
            cursor.execute(query, (ticket_id, session['username']))
            ticket = cursor.fetchone()

            cursor.close()
            conn.close()

            if ticket:
                status = ticket['status']
                return render_template('check_ticket_status.html', status=status)
            else:
                return render_template('check_ticket_status.html', status='Ticket not found.')

        return render_template('check_ticket_status.html', status='')
    return redirect(url_for('home'))

@app.route('/track_ticket', methods=['GET', 'POST'])
def track_ticket():
    if 'role' in session and session['role'] == 'client':
        if request.method == 'POST':
            ticket_id = request.form['ticket_id']
            conn = get_db_connection()
            cursor = conn.cursor()

            query = 'SELECT status FROM tickets WHERE id = ? AND username = ?'
            cursor.execute(query, (ticket_id, session['username']))
            ticket = cursor.fetchone()

            cursor.close()
            conn.close()

            if ticket:
                status = ticket['status']
                return render_template('track_ticket.html', status=status)
            else:
                return render_template('track_ticket.html', status='Ticket not found.')

        return render_template('track_ticket.html', status='')
    return redirect(url_for('home'))

@app.route('/send_feedback', methods=['GET', 'POST'])
def send_feedback():
    if 'role' in session and session['role'] == 'client':
        if request.method == 'POST':
            feedback = request.form['feedback']
            ticket_id = request.form['ticket_id']

            # Connect to SQLite and save the feedback
            conn = get_db_connection()
            cursor = conn.cursor()

            query = 'INSERT INTO feedback (ticket_id, username, feedback) VALUES (?, ?, ?)'
            cursor.execute(query, (ticket_id, session['username'], feedback))
            conn.commit()

            cursor.close()
            conn.close()

            return render_template('send_feedback.html', result='Feedback submitted successfully.')

        return render_template('send_feedback.html', result='')
    return redirect(url_for('home'))

@app.route('/rate_service', methods=['GET', 'POST'])
def rate_service():
    if 'role' in session and session['role'] == 'client':
        if request.method == 'POST':
            rating = request.form['rating']
            ticket_id = request.form['ticket_id']

            # Connect to SQLite and save the rating
            conn = get_db_connection()
            cursor = conn.cursor()

            query = 'INSERT INTO ratings (ticket_id, username, rating) VALUES (?, ?, ?)'
            cursor.execute(query, (ticket_id, session['username'], rating))
            conn.commit()

            cursor.close()
            conn.close()

            return render_template('rate_service.html', result='Rating submitted successfully.')

        return render_template('rate_service.html', result='')
    return redirect(url_for('home'))

