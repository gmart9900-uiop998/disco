import requests
import re
import time

class SmartTempMail:
    def __init__(self):
        self.base_url = "https://www.1secmail.com/api/v1/"
        self.email = None
        self.login = None
        self.domain = None
    
    def generate_email(self):
        """Generate temporary email"""
        response = requests.get(f"{self.base_url}?action=genRandomMailbox&count=1")
        self.email = response.json()[0]
        self.login, self.domain = self.email.split('@')
        print(f"✉️  Email: {self.email}")
        return self.email
    
    def get_messages(self):
        """Get inbox messages"""
        response = requests.get(
            f"{self.base_url}?action=getMessages&login={self.login}&domain={self.domain}"
        )
        return response.json()
    
    def read_message(self, message_id):
        """Read specific message"""
        response = requests.get(
            f"{self.base_url}?action=readMessage&login={self.login}&domain={self.domain}&id={message_id}"
        )
        return response.json()
    
    def extract_verification_code(self, text):
        """Extract common verification code patterns"""
        patterns = [
            r'\b(\d{6})\b',  # 6-digit code
            r'\b(\d{4})\b',  # 4-digit code
            r'code:\s*(\w+)',  # "code: XXXXX"
            r'verification code:\s*(\w+)',
            r'OTP:\s*(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def wait_for_verification_code(self, timeout=60):
        """Wait and auto-extract verification code"""
        print("🔍 Waiting for verification code...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            messages = self.get_messages()
            
            if messages:
                for msg in messages:
                    full_msg = self.read_message(msg['id'])
                    body = full_msg.get('textBody', full_msg.get('body', ''))
                    
                    code = self.extract_verification_code(body)
                    if code:
                        print(f"✅ Verification Code Found: {code}")
                        return code
            
            time.sleep(5)
        
        print("⏱️  Timeout - No code found")
        return None


# Example Usage
if __name__ == "__main__":
    mail = SmartTempMail()
    
    # Generate email
    email = mail.generate_email()
    
    # Use this email to sign up somewhere, then:
    code = mail.wait_for_verification_code(timeout=120)
    
    if code:
        print(f"\n🎉 Use this code: {code}")
