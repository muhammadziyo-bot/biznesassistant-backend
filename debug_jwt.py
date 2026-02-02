"""
Debug JWT token
"""

import jwt
from app.config import settings

def debug_jwt():
    """Debug JWT token content"""
    # Test token from login
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0MkBhZG1pbi5jb20iLCJ0ZW5hbnRfaWQiOjIsImV4cCI6MTczNzg4NzQ3NH0.example"
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print("JWT Payload:")
        for key, value in payload.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error decoding JWT: {e}")
    
    # Test with a real login
    import requests
    
    login_data = {
        'username': 'test2@admin.com',
        'password': 'test123'
    }
    
    response = requests.post('http://localhost:8000/api/auth/login', data=login_data)
    
    if response.status_code == 200:
        token = response.json()['access_token']
        print(f"\nReal token: {token[:50]}...")
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            print("Real JWT Payload:")
            for key, value in payload.items():
                print(f"  {key}: {value} ({type(value)})")
        except Exception as e:
            print(f"Error decoding real JWT: {e}")
    else:
        print(f"Login failed: {response.status_code}")

if __name__ == "__main__":
    debug_jwt()
