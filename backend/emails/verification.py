import smtplib as smt
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import dotenv

dotenv.load_dotenv()

smtp_server = 'smtp.gmail.com'
smtp_port = 587
provider = os.getenv("moon_analyzer_provider")  # Ensure valid sender email
emps = os.getenv('moon_analyzer_emps')

def send_verification_email(username, usermail, otp):
    msg = MIMEMultipart('alternative')  # Dual format (HTML and Plain Text)
    msg['From'] = provider
    msg['To'] = usermail
    msg['Subject'] = "Verify Your Email Address"
    msg['Reply-To'] = provider  # Valid reply address
    msg['X-Mailer'] = 'Python-Mailer'  # Custom header to avoid spam triggers
    msg['X-Priority'] = '3'  # Priority should not be set to 1 unless necessary

    # Plain text version (important for spam avoidance)
    plain_content = f"""
    Hello {username},
    
    Welcome to MoonAnalyzer!

    Please verify your email address by using the verification code below:
    Verification Code: {otp}

    If you did not sign up for this account, please disregard this email.

    Thanks,
    MoonAnalyzer Team
    """

    # HTML version (with minimal, clean design)
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            h2 {{
                color: #333;
                text-align: center;
            }}
            .message {{
                font-size: 16px;
                color: #555;
                text-align: center;
            }}
            .otp {{
                font-size: 20px;
                font-weight: bold;
                text-align: center;
                margin: 20px 0;
                padding: 10px;
                background-color: #f0f0f0;
                border-radius: 6px;
            }}
            .footer {{
                text-align: center;
                font-size: 12px;
                color: #888;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Welcome to MoonAnalyzer!</h2>
            <p class="message">Hi {username},</p>
            <p class="message">Please verify your email address by using the verification code below:</p>
            <div class="otp">{otp}</div>
            <p class="message">If you did not sign up for this account, please ignore this email.</p>
            <div class="footer">
                Thanks,<br>
                MoonAnalyzer Team
            </div>
        </div>
    </body>
    </html>
    """

    # Attach both plain and HTML content
    msg.attach(MIMEText(plain_content, 'plain'))
    msg.attach(MIMEText(html_content, 'html'))

    # SMTP connection
    try:
        s = smt.SMTP(smtp_server, smtp_port)
        s.starttls()
        s.login(provider, emps)
        s.sendmail(provider, usermail, msg.as_string())
    finally:
        s.quit()


