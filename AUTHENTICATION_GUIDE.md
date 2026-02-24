# Authentication System Documentation

## Overview
The application now includes a complete user authentication system with login and registration functionality.

## Features

### 1. User Registration
- **Access**: Click the "📝 Register" button on the home page
- **Required Fields**:
  - Username (minimum 3 characters)
  - Email (valid email format)
  - Password (minimum 6 characters)
  - Confirm Password
  - Role Selection:
    - Company_Manager
    - Data Analytics
    - Vice President
    - CEO
    - Owner
  - Company Name
  - Company ID
  - Contact Number (Company)

### 2. User Login
- **Access**: Click the "🔑 Login" button on the home page
- **Required Fields**:
  - Username
  - Password

### 3. User Profile Display
- Once logged in, user information is displayed:
  - In the top-right corner of the home page
  - In the sidebar with username, role, and company name
  
### 4. Logout
- Click the "🚪 Logout" button to end your session

## Database Structure

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(100) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_id VARCHAR(100) NOT NULL,
    contact_number VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

## Security Features
- Passwords are hashed using SHA256 before storage
- No plain-text passwords are stored in the database
- Username and email uniqueness is enforced
- Password confirmation during registration

## Files Modified/Created

### New Files:
1. `utils/auth.py` - Authentication utilities
2. `pages/login_page.py` - Login page UI
3. `pages/register_page.py` - Registration page UI
4. `setup_auth.py` - Database setup script

### Modified Files:
1. `database/models.py` - Added User model
2. `database/schema.sql` - Added users table
3. `pages/home_page.py` - Added login/logout buttons
4. `pages/__init__.py` - Imported new pages
5. `app.py` - Added authentication flow and user info display

## Setup Instructions

### First Time Setup:
1. Run the database setup script:
   ```bash
   python setup_auth.py
   ```

2. Start the application:
   ```bash
   streamlit run app.py
   ```

3. Click "Register" and create your first user account

### Usage Flow:
1. **New User**: Register → Login → Access application
2. **Existing User**: Login → Access application
3. **Logout**: Click logout button when done

## Session Management
- User session is maintained using Streamlit's session state
- Login status persists across page navigation
- Logout clears all user session data

## Future Enhancements
- Password reset functionality
- Email verification
- Role-based access control (RBAC)
- Multi-factor authentication (MFA)
- Session timeout
- User profile editing
- Admin panel for user management

## Troubleshooting

### Database Connection Issues:
- By default, the app uses SQLite (business_analytics.db)
- If you prefer PostgreSQL, set `USE_POSTGRES=true` in environment

### Can't Register:
- Ensure username and email are unique
- Check password meets minimum requirements
- Verify all required fields are filled

### Can't Login:
- Verify username and password are correct
- Check if account is active
- Ensure database is properly initialized

## API Reference

### Authentication Functions (utils/auth.py):

```python
# Register a new user
success, message = register_user(username, email, password, role, 
                                 company_name, company_id, contact_number)

# Login user
success, user_data = login_user(username, password)

# Logout user
logout_user()

# Check if logged in
if is_logged_in():
    user = get_current_user()

# Require authentication (decorator)
require_auth()
```

## Contact & Support
For issues or questions about the authentication system, please refer to the main project documentation or create an issue in the project repository.
