from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = '1234'  # Set a secret key for session management

# Database connection function for SQLite
def get_db_connection():
    conn = sqlite3.connect('database.db')  # Connects to an SQLite database file
    conn.row_factory = sqlite3.Row  # Enables row access by column name
    return conn

@app.route('/agent/view_tickets', methods=['GET', 'POST'])
def agent_view_tickets():
    if 'role' in session and session['role'] == 'agent':
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to retrieve all unassigned tickets
        query = 'SELECT * FROM tickets WHERE status = ? AND assigned_agent IS NULL'
        cursor.execute(query, ('Pending',))
        tickets = cursor.fetchall()

        if request.method == 'POST':
            ticket_id = request.form['ticket_id']
            priority = request.form['priority']
            category = request.form['category']

            # Update ticket with priority and category
            update_query = '''UPDATE tickets 
                              SET priority = ?, category = ?, assigned_agent = ? 
                              WHERE id = ?'''
            cursor.execute(update_query, (priority, category, session['username'], ticket_id))
            conn.commit()

            # Insert a notification for the agent
            notification_message = f"Ticket {ticket_id} has been assigned to you with priority {priority} and category {category}."
            notification_query = '''INSERT INTO agent_notifications (agent_id, ticket_id, notification_message, date_time)
                                    VALUES (?, ?, ?, ?)'''
            cursor.execute(notification_query, (session['user_id'], ticket_id, notification_message, datetime.now()))
            conn.commit()

        cursor.close()
        conn.close()
        return render_template('agent_assign_ticket.html', tickets=tickets)
    return redirect(url_for('home'))

@app.route('/assign_ticket', methods=['POST'])
def assign_ticket():
    if 'role' in session and session['role'] == 'admin':
        ticket_id = request.form['ticket_id']
        ticket_type = request.form['ticket_type']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Find an agent based on ticket type (this logic can be customized further)
        query = 'SELECT * FROM agents WHERE role = ? AND assigned_ticket IS NULL'
        if ticket_type == 'Electric failure':
            cursor.execute(query, ('Technician',))
        elif ticket_type == 'Street cleaning':
            cursor.execute(query, ('Cleaner',))
        else:
            cursor.execute(query, ('General Agent',))

        agent = cursor.fetchone()

        if agent:
            # Assign ticket to the agent
            update_query = 'UPDATE tickets SET assigned_agent = ? WHERE id = ?'
            cursor.execute(update_query, (agent['username'], ticket_id))
            conn.commit()

            # Insert notification for the agent
            notification_message = f"Ticket {ticket_id} has been assigned to you."
            notification_query = '''INSERT INTO agent_notifications (agent_id, ticket_id, notification_message, date_time)
                                    VALUES (?, ?, ?, ?)'''
            cursor.execute(notification_query, (agent['id'], ticket_id, notification_message, datetime.now()))
            conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('home'))
    return redirect(url_for('home'))

@app.route('/agent/notifications')
def agent_notifications():
    if 'role' in session and session['role'] == 'agent':
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all notifications for the agent
        query = 'SELECT * FROM agent_notifications WHERE agent_id = ? ORDER BY date_time DESC'
        cursor.execute(query, (session['user_id'],))
        notifications = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('agent_notifications.html', notifications=notifications)
    return redirect(url_for('home'))

@app.route('/agent/prioritize_ticket', methods=['GET', 'POST'])
def prioritize_ticket():
    if 'role' in session and session['role'] == 'agent':
        if request.method == 'POST':
            ticket_id = request.form['ticket_id']
            priority = request.form['priority']  # 'High', 'Medium', 'Low'
            category = request.form['category']  # e.g., 'Maintenance', 'Electric failure'

            conn = get_db_connection()
            cursor = conn.cursor()

            # Update the ticket's priority and category
            update_query = '''UPDATE tickets SET priority = ?, category = ? WHERE id = ?'''
            cursor.execute(update_query, (priority, category, ticket_id))
            conn.commit()

            cursor.close()
            conn.close()

            return redirect(url_for('agent_view_tickets'))

        return render_template('prioritize_ticket.html')
    return redirect(url_for('home'))

