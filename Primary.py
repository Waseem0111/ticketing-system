from flask import Flask, request, render_template, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = '1234'

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')  # Connects to the database file
    conn.row_factory = sqlite3.Row  # Enables dictionary-like access to rows
    return conn

# Route for sign-up page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Validate the role to only allow 'Client' or 'Agent'
        if role not in ['Client', 'Agent']:
            flash('Invalid role selected.', 'error')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, hashed_password, role))
            conn.commit()
            conn.close()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))  # Redirect to the login page after successful sign-up
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different one.', 'error')
            conn.close()
            return redirect(url_for('signup'))

    return render_template('signup.html')

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        # Check if user exists and password is correct
        if user:
            if check_password_hash(user['password'], password):
                session['username'] = username
                session['role'] = user['role']  # Store the role in the session
                flash('Login successful!', 'success')

                # Debugging statement
                print(f"Logged in user: {session['username']} with role: {session['role']}")

                # Redirect based on role
                if user['role'] == 'Admin' and username == 'admin':  # Match the specific admin username
                    return redirect(url_for('admin_dashboard'))
                elif user['role'] == 'Client':
                    return redirect(url_for('client_dashboard'))
                elif user['role'] == 'Agent':
                    return redirect(url_for('agent_dashboard'))
                else:
                    flash('Role not recognized. Access denied.', 'error')
                    return redirect(url_for('login'))
            else:
                flash('Incorrect password. Please try again.', 'error')
        else:
            flash('Username not found. Please check your username or sign up.', 'error')

        return redirect(url_for('login'))

    return render_template('login.html')

# Route for logout
@app.route('/logout',methods=['GET','POST'])
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Default route
@app.route('/')
def home():
    return redirect(url_for('login'))  # Redirects to the login page by default

@app.route('/select_role', methods=['POST'])
def select_role():
    # Retrieve the role and username from the form data
    role = request.form.get('role')
    username = request.form.get('username')

    if role and username:
        # Store the role and username in the session
        session['role'] = role
        session['username'] = username

        # Redirect to the appropriate dashboard based on the selected role
        if role == 'Client':
            return redirect(url_for('client_dashboard'))
        elif role == 'Agent':
            return redirect(url_for('agent_dashboard'))
        elif role == 'Admin':
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid role selected.", 'error')
            return redirect(url_for('home'))
    else:
        flash("Role or username not provided.", 'error')
        return redirect(url_for('home'))


@app.route('/client_dashboard')
def client_dashboard():
    if 'role' in session and session['role'] == 'Client':
        conn = get_db_connection()
        tickets = conn.execute('SELECT * FROM tickets WHERE username = ?', (session.get('username'),)).fetchall()
        conn.close()
        return render_template('client_dashboard.html', tickets=tickets)
    return redirect(url_for('home'))

@app.route('/track_and_history', methods=['GET', 'POST'])
def track_and_history():
    if 'role' in session and session['role'] == 'Client':
        conn = get_db_connection()
        username = session.get('username')

        # Get all tickets from the client
        tickets = conn.execute('SELECT * FROM tickets WHERE username = ?', (username,)).fetchall()

        if request.method == 'POST':
            ticket_id = request.form['ticket_id']  # Get ticket ID from the form input

            # Fetch the ticket based on ticket ID and logged-in client's username
            ticket = conn.execute(
                'SELECT * FROM tickets WHERE id = ? AND username = ?',
                (ticket_id, session['username'])
            ).fetchone()
            
            conn.close()

            if ticket:
                return render_template('track_and_history.html', tickets=tickets, ticket=ticket)
            else:
                flash('No ticket found with the provided ID or it doesn\'t belong to you.', 'error')
                return render_template('track_and_history.html', tickets=tickets)

        conn.close()
        return render_template('track_and_history.html', tickets=tickets)

    return redirect(url_for('home'))

@app.route('/agent_dashboard')
def agent_dashboard():
    if 'role' in session and session['role'] == 'Agent':
        conn = get_db_connection()
        tickets = conn.execute('SELECT * FROM tickets WHERE assigned_agent = ?', (session.get('username'),)).fetchall()
        conn.close()
        return render_template('agent_dashboard.html', tickets=tickets)
    return redirect(url_for('home'))

@app.route('/admin_dashboard')
def admin_dashboard():
        conn = get_db_connection()
        feedbacks = conn.execute('SELECT * FROM feedback').fetchall()
        conn.close()
        return render_template('admin_dashboard.html', feedbacks=feedbacks)
@app.route('/submit_ticket', methods=['GET', 'POST'])
def submit_ticket():
    if 'role' in session and session['role'] == 'Client':
        if request.method == 'POST':
            username = session.get('username')
            ticket_type = request.form.get('ticket_type')
            custom_ticket_type = request.form.get('custom_ticket_type')  # Get the custom type if provided
            description = request.form.get('description')
            submission_channel = 'Web'
            submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Use the custom type if 'Other' was selected
            if ticket_type == 'Other' and custom_ticket_type:
                ticket_type = custom_ticket_type

            conn = get_db_connection()
            try:
                conn.execute('''
                    INSERT INTO tickets (username, ticket_type, description, submission_channel, status, submission_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, ticket_type, description, submission_channel, 'Pending', submission_time))
                conn.commit()
                conn.close()

                flash('Your ticket has been successfully submitted!', 'success')
                return redirect(url_for('view_ticket_details'))
            except sqlite3.Error as e:
                print("Error inserting ticket:", e)
                flash(f"An error occurred while submitting the ticket: {e}", 'error')
                return redirect(url_for('submit_ticket'))

        return render_template('submit_ticket.html')

    return redirect(url_for('home'))

@app.route('/send_feedback', methods=['GET', 'POST'])
def send_feedback():
    if 'role' in session and session['role'] == 'Client':
        conn = get_db_connection()
        username = session.get('username')
        
        # Fetch tickets submitted by the logged-in client
        user_tickets = conn.execute('SELECT * FROM tickets WHERE username = ?', (username,)).fetchall()
        conn.close()

        if request.method == 'POST':
            ticket_id = request.form['ticket_id']
            feedback = request.form['feedback']
            rating = request.form['rating']

            conn = get_db_connection()
            try:
                # Insert feedback into the feedback table
                conn.execute('''
                    INSERT INTO feedback (ticket_id, username, feedback, rating)
                    VALUES (?, ?, ?, ?)
                ''', (ticket_id, username, feedback, rating))
                conn.commit()
                conn.close()

                flash('Feedback submitted successfully!', 'success')
                return redirect(url_for('client_dashboard'))
            except sqlite3.Error as e:
                flash(f"An error occurred while submitting feedback: {e}", 'error')
                conn.close()
        
        return render_template('send_feedback.html', user_tickets=user_tickets)
    else:
        return redirect(url_for('home'))

@app.route('/view_feedback')
def view_feedback():
        conn = get_db_connection()
        feedbacks = conn.execute('SELECT * FROM feedback').fetchall()
        conn.close()
        return render_template('view_feedback.html', feedbacks=feedbacks)
@app.route('/agent_ticket_maneger')
def ticket_maneger():
    conn = get_db_connection()
    tickets = conn.execute('SELECT * FROM tickets').fetchall()
    conn.close()
    return render_template('agent_ticket_maneger.html', tickets=tickets)

# Updated route to include a debug statement
@app.route('/agent_assign_ticket', methods=['GET', 'POST'])
def agent_assign_ticket():
    if 'role' in session and session['role'] == 'Agent':
        conn = get_db_connection()
        
        # Fetch all tickets, regardless of assigned_agent status
        all_tickets = conn.execute("SELECT * FROM tickets").fetchall()
        
        # Print all tickets for debugging
        print("All Tickets:", all_tickets)
        
        # Fetch agents from the users table where role is 'Agent'
        agents = conn.execute("SELECT username FROM users WHERE role = 'Agent'").fetchall()
        
        conn.close()
        
        # Handle POST request if the form is submitted
        if request.method == 'POST':
            ticket_id = request.form.get('ticket_id')
            assigned_agent = request.form.get('assigned_agent')
            priority = request.form.get('priority')
            category = request.form.get('category')
            
            conn = get_db_connection()
            try:
                # Update the ticket with the assigned agent, priority, and category
                conn.execute(
                    "UPDATE tickets SET assigned_agent = ?, priority = ?, category = ? WHERE id = ?",
                    (assigned_agent, priority, category, ticket_id)
                )
                conn.commit()
                conn.close()
                flash('Ticket assigned successfully!', 'success')
                return redirect(url_for('agent_assign_ticket'))
            except sqlite3.Error as e:
                flash(f"Error assigning ticket: {e}", 'error')
                conn.close()
        
        return render_template('agent_assign_ticket.html', all_tickets=all_tickets, agents=agents)
    else:
        return redirect(url_for('home'))

@app.route('/updatetickets', methods=['POST'])
def update_tickets():
    if 'role' in session and session['role'] == 'Agent':
        conn = get_db_connection()
        try:
            # Get the list of ticket IDs from the form
            ticket_ids = request.form.getlist('ticket_id')
            
            for ticket_id in ticket_ids:
                # Get form values for each ticket ID
                client_name = request.form.get(f'client_name{ticket_id}')
                ticket_type = request.form.get(f'ticket_type{ticket_id}')
                status = request.form.get(f'status{ticket_id}')
                assigned_to = request.form.get(f'assignedto{ticket_id}')

                # Update the ticket in the database
                conn.execute('''
                    UPDATE tickets
                    SET username = ?, ticket_type = ?, status = ?, assigned_agent = ?
                    WHERE id = ?
                ''', (client_name, ticket_type, status, assigned_to, ticket_id))

            conn.commit()
            flash('Tickets have been successfully updated!', 'success')
        except sqlite3.Error as e:
            print("Error updating tickets:", e)
            flash(f"An error occurred while updating tickets: {e}", 'error')
        finally:
            conn.close()

        # Redirect to the correct route
        return redirect(url_for('ticket_maneger'))
    else:
        return redirect(url_for('home'))

@app.route('/view_ticket_details',methods=['GET', 'POST'])
def view_ticket_details():
    if 'role' in session and session['role'] == 'Client':
        username = session.get('username')
        conn = get_db_connection()
        ticket = conn.execute("SELECT * FROM tickets WHERE username = ? ORDER BY id DESC LIMIT 1", (username,)).fetchone()
        conn.close()
        
        if ticket:
            return render_template('view_ticket_details.html', ticket=ticket)
        else:
            flash("No ticket details available.", "info")
            return redirect(url_for('client_dashboard'))

    return redirect(url_for('home'))

@app.route('/admin_ticket_maneger')
def ticket_maneger3():
    conn = get_db_connection()
    tickets = conn.execute('SELECT * FROM tickets').fetchall()
    conn.close()
    return render_template('admin_ticket_maneger.html', tickets=tickets)


@app.route('/Reporting', methods=['GET', 'POST'])
def Reporting():
    report_type = None  # Initialize report type variable
    ticket_summary_data = []
    agent_performance_data = []

    if request.method == 'POST':
        report_type = request.form.get('report_type')

        conn = get_db_connection()

        # Generate Ticket Summary Report
        if report_type == 'ticket_summary_data':
            ticket_summary_data = conn.execute('''
                SELECT 
                    ticket_type, 
                    status, 
                    COUNT(*) AS count
                FROM 
                    tickets
                GROUP BY 
                    ticket_type, 
                    status
            ''').fetchall()

        # Generate Agent Performance Report
        elif report_type == 'agent_performance_data':
            agent_performance_data = conn.execute('''
                SELECT 
                    assigned_agent, 
                    COUNT(*) AS total_tickets, 
                    SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_tickets
                FROM 
                    tickets
                WHERE 
                    assigned_agent IS NOT NULL
                GROUP BY 
                    assigned_agent
            ''').fetchall()

        conn.close()

    return render_template(
        'Reporting.html',
        report_type=report_type,
        ticket_summary=ticket_summary_data,
        agent_performance=agent_performance_data
    )




if __name__ == '__main__':
    app.run(debug=True)
