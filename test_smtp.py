import smtplib

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "adithyancoding@gmail.com"
SENDER_PASSWORD = "famn yqnn rjlz lhyl"

def test_smtp_connection():
    try:
        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.quit()
        print("SMTP login successful. App password is valid.")
        return True
    except Exception as e:
        print(f"SMTP login failed: {e}")
        return False

if __name__ == "__main__":
    test_smtp_connection()
