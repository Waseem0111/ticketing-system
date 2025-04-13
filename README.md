
# Ticketing System

A Flask-based web application for managing support tickets with three user roles: **Admin**, **Agent**, and **Client**.

## Features
- **Clients**  
  - Submit tickets with custom types.  
  - Track ticket status and history.  
  - Provide feedback and ratings.  
- **Agents**  
  - Assign, prioritize, and categorize tickets.  
  - Receive real-time notifications.  
  - Update ticket statuses.  
- **Admins**  
  - View system-wide reports (ticket summaries, agent performance).  
  - Manage all tickets and feedback.  

## Setup

### Prerequisites
- Python 3.7+
- pip

### Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/Waseem0111/ticketing-system.git
   cd ticketing-system
   ```

2. **Install dependencies**:
   ```bash
   pip install flask werkzeug
   ```

3. **Initialize the database** (creates SQLite DB and admin user):
   ```bash
   python setup_admin.py
   ```

4. **Run the application**:
   ```bash
   python Primary.py
   ```
   - Access the app at `http://localhost:5000`.

## Usage
- **Roles**:  
  - Admins: Access `/admin_dashboard` for reports.  
  - Agents: Access `/agent_dashboard` to manage tickets.  
  - Clients: Submit tickets via `/submit_ticket`.  

## Project Structure
```
ticketing-system/
├── Primary.py          # Main application entry point
├── Agents.py           # Agent-specific routes
├── Clients.py          # Client-specific routes
├── admin.py            # Admin-specific routes
├── setup_admin.py      # DB initialization script
├── templates/          # HTML templates (not shown in your files)
├── database.db         # SQLite database (created after setup)
└── README.md           # This file
```

## License
MIT
