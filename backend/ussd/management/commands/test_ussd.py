import sys
from django.core.management.base import BaseCommand
from ussd.handler import USSDHandler, create_session

# Ensure UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

log_file = open("ussd_debug.log", "w", encoding="utf-8")

def log(msg):
    log_file.write(str(msg) + "\n")
    log_file.flush()

class Command(BaseCommand):
    help = 'Test USSD handler logic'
    
    def handle(self, *args, **options):
        self.stdout.write("Testing USSD Handler...")
        
        # Test cases
        test_cases = [
            {"steps": [""], "expected": "Karibu HudumaAfya"},
            {"steps": ["1"], "expected": "Tafuta kwa"},
            {"steps": ["1", "1"], "expected": "Andika jina la kaunti"},
            {"steps": ["1", "1", "Nairobi"], "expected": "Matokeo"},
            {"steps": ["1", "1", "Nairobi", "1"], "expected": "Kenyatta National Hospital"},
        ]
        
        for idx, test in enumerate(test_cases):
            self.stdout.write(f"\nTest Case {idx + 1}: {' -> '.join(test['steps']) if test['steps'][0] else 'Main Menu'}")
            log(f"--- Test Case {idx + 1} ---")
            
            # Create fresh session for each test case
            session = create_session(f"test_{idx}", "254712345678")
            handler = USSDHandler(session)
            
            response = ""
            current_text_array = []
            
            # Simulate sequential input to build state
            for step in test['steps']:
                log(f"STEP: {step}, current_text_array={current_text_array}, level={session.get('menu_level')}")
                if step:
                    current_text_array.append(step)
                
                # IMPORTANT: In a real USSD app, the handler is usually stateless 
                # but the session dictionary it modifies IS stateful.
                # We need to make sure the session is updated.
                response = handler.process_input(current_text_array, step)
                log(f"RESPONSE: {response[:50]}")
                
                # Re-initialize handler with the same session to simulate state persistence
                # though technically the dict is shared, some implementations might cache local vars.
                handler = USSDHandler(session)
            
            # Check response
            if test['expected'].lower() in response.lower():
                self.stdout.write(f"Passed: {response[:50].replace('\n', ' ')}...")
            else:
                self.stdout.write(f"Failed! Expected: {test['expected']}")
                self.stdout.write(f"Actual Response: {response}")
                log(f"FAILED! Expected: {test['expected']}, Actual: {response}")
        
        self.stdout.write("\nUSSD handler tests completed!")
        log_file.close()