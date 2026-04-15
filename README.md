# Everix Demo Backend

Flask backend powering the Everix Growth System live demo.

## What it does
- **Speed-to-Lead**: Fires a real SMS to a prospect within seconds of form submission
- **SMS Booking**: Handles inbound SMS replies with a full booking conversation flow
- **Demo Booking**: Sends booking confirmation SMS

## Deploy to Render (new account: williamkmilson@gmail.com)

1. Push this folder to a new GitHub repo (e.g. `everixautomation/everix-demo-backend`)
2. Log in to render.com with williamkmilson@gmail.com
3. Click **New → Web Service** → connect GitHub → select this repo
4. Set these environment variables in Render dashboard:

| Variable | Where to find it |
|---|---|
| `TWILIO_ACCOUNT_SID` | twilio.com/console → Account Info |
| `TWILIO_AUTH_TOKEN` | twilio.com/console → Account Info |
| `TWILIO_PHONE_NUMBER` | twilio.com/console → Phone Numbers (format: +16471234567) |
| `ALLOWED_ORIGIN` | `https://everixautomation.com` |

5. After deploy, copy your Render URL (e.g. `https://everix-demo-backend.onrender.com`)
6. Paste it into `demo.html` on your website:
   ```js
   const BACKEND_URL = 'https://everix-demo-backend.onrender.com';
   ```

## Twilio Inbound SMS Setup
In twilio.com/console → Phone Numbers → your number → Messaging:
- Set webhook URL to: `https://everix-demo-backend.onrender.com/api/sms/inbound`
- Method: HTTP POST
