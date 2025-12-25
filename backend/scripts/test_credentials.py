import africastalking

USERNAME = "sandbox"
API_KEY = "atsk_b8d731cae5157044bda8513bc68c4d304a9c5a131c7974a8c38696a55662561c35c624a2"


try:
    africastalking.initialize(USERNAME, API_KEY)
   
    sms = africastalking.SMS
    
    print("✅ Credentials are VALID!")

    print(f"Response: {sms.send("Test from Kenya Health", ["+254711082904"])}")
    

except Exception as e:

    print(f"❌ Error: {e}")

    print("\nTroubleshooting:")

    print("1. Make sure you copied the ENTIRE API key")

    print("2. Check your username is correct")

    print("3. Ensure you're using SANDBOX credentials, not production")