import smtplib as smt
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def mailSender(username, usermail, otp):
    smpt_server = 'smtp.gmail.com'
    smtp_port = 587
    provider = os.getenv("---")#provider email here
    emps = os.getenv('---')#provide the password for mail
    msg = MIMEMultipart()
    #html code to beautify the mail
    btn = f"""
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
                margin: 50px auto;
                background-color: #ffffff;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}

            h2 {{
                color: #333333;
                text-align: center;
            }}

            .otp {{
                font-size: 24px;
                font-weight: bold;
                text-align: center;
                padding: 20px;
                background-color: #e0e0e0;
                border-radius: 6px;
                margin: 20px 0;
            }}

            .message {{
                font-size: 16px;
                color: #555555;
                text-align: center;
            }}

            .ignore {{
                font-size: 14px;
                color: #888888;
                text-align: center;
                margin-top: 20px;
            }}

            .footer {{
                margin-top: 30px;
                font-size: 12px;
                color: #aaaaaa;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Password Reset Request</h2>
            <p class="message">Hey {username}, Please use the OTP below to reset your password:</p>
            <div class="otp">{otp}</div>
            <p class="ignore">If you did not request a password reset, please ignore this email.</p>
            <div class="footer">
                &copy; 2024 UniAlgo. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    #smtplibe parameters
    msg['From'] = provider
    msg['To'] = usermail
    msg['Subject'] = "Reset your Password"
    msg.attach(MIMEText(btn, 'html'))
    s = smt.SMTP(smpt_server,smtp_port)
    try:
        s.starttls()
        s.login(provider,emps)
        s.sendmail(provider, usermail, msg.as_string())
    finally:    
        s.quit()

def main():
    otp = input("Enter otp :")
    usermail =input("Enter the mail:")
    mailSender('<User name here>', usermail, otp)
    print("mail sent to", usermail)

main()