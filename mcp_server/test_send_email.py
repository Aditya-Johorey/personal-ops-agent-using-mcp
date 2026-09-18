from dotenv import load_dotenv
load_dotenv()

from gmail import send_email

if __name__ == "__main__":
    your_email = input("Enter YOUR OWN email address to test with: ")
    result = send_email(
        to=your_email,
        subject="Test from MCP project",
        body="This is a test email sent via the Gmail API from my MCP server.",
    )
    print(result)