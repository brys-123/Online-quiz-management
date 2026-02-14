# Email Configuration Guide

The quiz system can now send confirmation emails to admins when they register.

## Setup Instructions

### Option 1: Gmail (Recommended)

**Step 1:** Generate a Gmail App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Sign in to your Google account
3. Select "Mail" and "Windows Computer"
4. Click "Generate"
5. Copy the 16-character password (it will look like: `xxxx xxxx xxxx xxxx`)

**Step 2:** Set Environment Variables

**On Windows (PowerShell):**
```powershell
$env:SMTP_EMAIL = "your-gmail@gmail.com"
$env:SMTP_PASSWORD = "xxxx xxxx xxxx xxxx"  # Your 16-char app password
$env:SMTP_SERVER = "smtp.gmail.com"
$env:SMTP_PORT = "587"
```

Then restart the Flask app in the same terminal.

**Option 2: Alternative Email Provider**

If using Outlook, SendGrid, or another provider:
```powershell
$env:SMTP_EMAIL = "your-email@outlook.com"
$env:SMTP_PASSWORD = "your-password"
$env:SMTP_SERVER = "smtp-mail.outlook.com"  # Outlook example
$env:SMTP_PORT = "587"
```

## How to Verify It's Working

1. Register a new admin account via the admin login page
2. Check if you receive a confirmation email at the address you registered with
3. Flask console will show: `✓ Welcome email sent to admin@example.com`

## Troubleshooting

- **Gmail "Sign-in attempt blocked"**: Make sure you used an **App Password**, not your regular Gmail password
- **Connection timeout**: Check that SMTP server, email, and password are correct
- **Email not received**: Check spam/junk folder
- **No output in console**: Email credentials not set - return to Step 2

## Production Recommendation

For production use, store credentials in a `.env` file instead of environment variables:

**Create `.env` file in the same directory as `app.py`:**
```
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

Then install python-dotenv:
```cmd
pip install python-dotenv
```

And add to the top of app.py (after imports):
```python
from dotenv import load_dotenv
load_dotenv()
```
