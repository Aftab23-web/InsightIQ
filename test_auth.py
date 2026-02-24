"""
Test Authentication System
Quick test to verify the authentication works correctly
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import init_db, User, get_session
from utils.auth import register_user, login_user, hash_password

def test_auth():
    """Test authentication functions"""
    print(" Testing Authentication System...\n")
    
    # Initialize database
    print("1. Initializing database...")
    try:
        init_db()
        print("    Database initialized\n")
    except Exception as e:
        print(f"    Database initialization failed: {e}\n")
        return
    
    # Test user registration
    print("2. Testing user registration...")
    success, message = register_user(
        username="testuser",
        email="test@example.com",
        password="test123",
        role="CEO",
        company_name="Test Company",
        company_id="TC001",
        contact_number="+1234567890"
    )
    
    if success:
        print(f"    {message}\n")
    else:
        print(f"     {message} (may already exist)\n")
    
    # Test duplicate username
    print("3. Testing duplicate username validation...")
    success, message = register_user(
        username="testuser",
        email="another@example.com",
        password="test123",
        role="CEO",
        company_name="Test Company",
        company_id="TC001",
        contact_number="+1234567890"
    )
    
    if not success and "already exists" in message:
        print(f"    Duplicate validation working: {message}\n")
    else:
        print(f"    Duplicate validation not working properly\n")
    
    # Test login with correct credentials
    print("4. Testing login with correct credentials...")
    success, result = login_user("testuser", "test123")
    
    if success:
        print(f"    Login successful!")
        print(f"      Username: {result['username']}")
        print(f"      Role: {result['role']}")
        print(f"      Company: {result['company_name']}\n")
    else:
        print(f"    Login failed: {result}\n")
    
    # Test login with wrong password
    print("5. Testing login with wrong password...")
    success, result = login_user("testuser", "wrongpassword")
    
    if not success:
        print(f"    Correctly rejected: {result}\n")
    else:
        print(f"    Should have rejected wrong password\n")
    
    # Test login with non-existent user
    print("6. Testing login with non-existent user...")
    success, result = login_user("nonexistentuser", "test123")
    
    if not success:
        print(f"    Correctly rejected: {result}\n")
    else:
        print(f"    Should have rejected non-existent user\n")
    
    # Verify user in database
    print("7. Verifying user in database...")
    try:
        session = get_session()
        user = session.query(User).filter(User.username == "testuser").first()
        if user:
            print(f"    User found in database:")
            print(f"      ID: {user.id}")
            print(f"      Username: {user.username}")
            print(f"      Email: {user.email}")
            print(f"      Role: {user.role}")
            print(f"      Company: {user.company_name}")
            print(f"      Created: {user.created_at}\n")
        else:
            print("    User not found in database\n")
        session.close()
    except Exception as e:
        print(f"    Error querying database: {e}\n")
    
    print("=" * 50)
    print(" Authentication System Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_auth()
