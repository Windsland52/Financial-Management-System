import requests
from tkinter import messagebox

BASE_URL = "http://43.143.217.242:5000"
LOGIN_URL = f"{BASE_URL}/login"
TEST_URL = f"{BASE_URL}/test"

def test_api():
    username = "admin"
    password = "admin"
    session = requests.Session()
    
    # Login request
    response = session.post(LOGIN_URL, json={"username": username, "password": password})

    if response:
        messagebox.showinfo("Success", "Login successful")
        
        # Check cookies
        print("Cookies after login:", session.cookies)

        # Test API request
        response = session.get(TEST_URL)
        print("Cookies after test API:", session.cookies)

        
        messagebox.showinfo("Success", "API test successful")
        print("Response from test API:", response.text)
    else:
        messagebox.showerror("Error", "Login failed")

if __name__ == "__main__":
    test_api()
