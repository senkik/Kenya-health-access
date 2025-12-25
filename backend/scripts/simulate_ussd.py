import requests
import time

BASE_URL = "http://localhost:8000"  

def simulate_ussd_flow():
    """Simulate a complete USSD flow"""
    session_id = "sim_" + str(int(time.time()))
    phone = "254712345678"
    
    steps = [
        ("", "Main Menu"),
        ("1", "Search Menu"),
        ("1", "Enter County"),
        ("Nairobi", "Search Results"),
        ("1", "Facility Details"),
    ]
    
    text = ""
    for step_input, description in steps:
        if step_input:
            text = f"{text}*{step_input}" if text else step_input
        
        print(f"\n[{description}]")
        print(f"Input: {step_input}")
        print(f"Full text: {text}")
        
        response = send_ussd(session_id, phone, text)
        print(f"Response:\n{response}")
        print("-" * 50)
        
        time.sleep(1)

def send_ussd(session_id, phone_number, text):
    """Send USSD request"""
    data = {
        "sessionId": session_id,
        "phoneNumber": phone_number,
        "serviceCode": "*384#",
        "text": text,
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/ussd/callback/",
            data=data,
            timeout=10
        )
        return response.text
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    simulate_ussd_flow()