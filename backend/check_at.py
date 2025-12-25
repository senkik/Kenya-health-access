import africastalking
print(f"Attributes: {dir(africastalking)}")
try:
    africastalking.initialize('sandbox', 'fake')
    print("Initialized")
    print(f"USSD: {getattr(africastalking, 'USSD', 'Not Found')}")
    print(f"SMS: {getattr(africastalking, 'SMS', 'Not Found')}")
except Exception as e:
    print(f"Error: {e}")
