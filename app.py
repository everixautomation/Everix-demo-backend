"""
Everix Demo Backend
-------------------
Handles:
  - Speed-to-Lead SMS via Twilio
  - Inbound SMS webhook (for booking demo responses)
  - Booking confirmation via Twilio

Deploy to Render as a Web Service (Python).
Required environment variables (set in Render dashboard):
  TWILIO_ACCOUNT_SID   — from twilio.com/console
  TWILIO_AUTH_TOKEN    — from twilio.com/console
  TWILIO_PHONE_NUMBER  — your Twilio number, e.g. +16475551234
  ALLOWED_ORIGIN       — your website, e.g. https://everixautomation.com
"""

import os
import re
import logging
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

# ── APP SETUP ────────────────────────────────────────────────────────────
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS — only allow requests from your website
ALLOWED_ORIGIN = os.environ.get('ALLOWED_ORIGIN', '*')
CORS(app, origins=[ALLOWED_ORIGIN, 'http://localhost:*'])

# ── TWILIO CLIENT ────────────────────────────────────────────────────────
TWILIO_SID   = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_FROM  = os.environ.get('TWILIO_PHONE_NUMBER', '')

twilio = Client(TWILIO_SID, TWILIO_TOKEN) if TWILIO_SID and TWILIO_TOKEN else None

# ── IN-MEMORY BOOKING STATE ──────────────────────────────────────────────
# Tracks demo leads waiting for booking confirmation
# In production use a real database (Airtable, Supabase, Google Sheets)
pending_bookings = {}   # phone -> { name, business, step, timestamp }

# ── HELPERS ──────────────────────────────────────────────────────────────
def clean_phone(raw: str) -> str:
    """Normalize phone to E.164 format for Canada/US."""
    digits = re.sub(r'\D', '', raw)
    if len(digits) == 10:
        return '+1' + digits
    if len(digits) == 11 and digits.startswith('1'):
        return '+' + digits
    if digits.startswith('+'):
        return raw
    return '+' + digits

def send_sms(to: str, body: str) -> bool:
    """Send an SMS via Twilio. Returns True on success."""
    if not twilio:
        logger.warning('Twilio not configured — SMS not sent.')
        return False
    try:
        msg = twilio.messages.create(to=to, from_=TWILIO_FROM, body=body)
        logger.info('SMS sent to %s | SID: %s', to, msg.sid)
        return True
    except Exception as e:
        logger.error('Twilio error: %s', e)
        return False

# ── ROUTES ───────────────────────────────────────────────────────────────

@app.route('/', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'Everix Demo Backend'})


@app.route('/api/demo/speed-to-lead', methods=['POST'])
def speed_to_lead():
    """
    Called by demo.html when a prospect enters their name + phone.
    Fires a real speed-to-lead SMS within seconds.
    """
    data = request.get_json(force=True, silent=True) or {}
    name     = (data.get('name') or '').strip()
    phone    = (data.get('phone') or '').strip()
    business = (data.get('business') or 'your service').strip()

    if not name or not phone:
        return jsonify({'error': 'name and phone are required'}), 400

    try:
        to = clean_phone(phone)
    except Exception:
        return jsonify({'error': 'invalid phone number'}), 400

    # Speed-to-lead message — same as what a real client lead would receive
    message = (
        f"Hi {name}! I saw you just reached out about {business} — "
        f"I'm on it. Do you have 2 minutes for a quick call today, "
        f"or would you prefer we connect by text? — Everix AI"
    )

    ok = send_sms(to, message)

    # Store state for follow-up booking demo
    pending_bookings[to] = {
        'name': name,
        'business': business,
        'step': 'awaiting_response',
        'timestamp': datetime.utcnow().isoformat()
    }

    if ok:
        return jsonify({'success': True, 'message': 'Speed-to-lead SMS sent'})
    else:
        # Return success even if Twilio isn't configured so demo page works
        return jsonify({'success': True, 'message': 'Demo mode — Twilio not configured', 'demo': True})


@app.route('/api/sms/inbound', methods=['POST'])
def sms_inbound():
    """
    Twilio webhook — receives inbound SMS replies from leads.
    Set this URL in your Twilio console under:
      Phone Numbers → Your Number → Messaging → Webhook
    URL: https://your-render-service.onrender.com/api/sms/inbound
    """
    from_number = request.form.get('From', '')
    body        = (request.form.get('Body') or '').strip().upper()

    logger.info('Inbound SMS from %s: %s', from_number, body)

    resp = MessagingResponse()

    # Look up state for this number
    state = pending_bookings.get(from_number)

    if not state:
        # Unknown sender — send a generic helpful response
        resp.message(
            "Hi! You've reached Everix Automation. "
            "To book a demo or speak with someone, visit everixautomation.com "
            "or call 647-668-4020."
        )
        return str(resp), 200, {'Content-Type': 'text/xml'}

    name = state.get('name', 'there')
    step = state.get('step', '')

    # ── BOOKING DEMO FLOW ────────────────────────────────────────────────
    if step == 'awaiting_response':
        if body in ('YES', 'Y', 'TEXT', 'TEXT ME', 'PREFER TEXT'):
            # They want to proceed by text — offer time slots
            pending_bookings[from_number]['step'] = 'awaiting_slot'
            resp.message(
                f"Great, {name}! I can book you in right now. "
                f"Which works better — Tuesday at 2pm or Wednesday at 10am?"
            )
        elif body in ('CALL', 'CALL ME', 'PHONE'):
            resp.message(
                f"Perfect, {name}! Someone from our team will call you shortly at {from_number}. "
                f"While you wait, you can also visit everixautomation.com to learn more."
            )
            pending_bookings.pop(from_number, None)
        else:
            resp.message(
                f"Hi {name}! Do you have 2 minutes for a quick call, "
                f"or would you prefer to connect by text? Just reply CALL or TEXT."
            )

    elif step == 'awaiting_slot':
        if 'TUESDAY' in body or 'TUE' in body or '2PM' in body:
            pending_bookings[from_number]['step'] = 'confirmed'
            pending_bookings[from_number]['appointment'] = 'Tuesday at 2:00pm'
            resp.message(
                f"You're confirmed, {name}! Tuesday at 2:00pm — I've added it to the calendar. "
                f"I'll send you a reminder 24 hours before. "
                f"Reply CHANGE anytime if you need to reschedule."
            )
        elif 'WEDNESDAY' in body or 'WED' in body or '10AM' in body or '10' in body:
            pending_bookings[from_number]['step'] = 'confirmed'
            pending_bookings[from_number]['appointment'] = 'Wednesday at 10:00am'
            resp.message(
                f"You're confirmed, {name}! Wednesday at 10:00am — I've added it to the calendar. "
                f"I'll send you a reminder 24 hours before. "
                f"Reply CHANGE anytime if you need to reschedule."
            )
        else:
            resp.message(
                f"No problem! We have Tuesday at 2pm or Wednesday at 10am — which works for you, {name}?"
            )

    elif step == 'confirmed':
        if 'CHANGE' in body or 'RESCHEDULE' in body or 'CANCEL' in body:
            pending_bookings[from_number]['step'] = 'awaiting_slot'
            resp.message(
                f"Of course, {name}! Would Tuesday at 2pm or Wednesday at 10am work better?"
            )
        elif 'CONFIRM' in body or 'YES' in body or 'OK' in body:
            appt = state.get('appointment', 'your appointment')
            resp.message(
                f"Great, {name}! See you at {appt}. "
                f"If anything changes, just reply CHANGE and we'll sort it out."
            )
        else:
            appt = state.get('appointment', 'your appointment')
            resp.message(
                f"Your booking is confirmed for {appt}, {name}. "
                f"Reply CHANGE to reschedule or CANCEL to cancel."
            )
    else:
        resp.message(
            f"Hi {name}! Reply YES to proceed with booking, or call us at 647-668-4020."
        )

    return str(resp), 200, {'Content-Type': 'text/xml'}


@app.route('/api/demo/booking', methods=['POST'])
def booking_demo():
    """
    Optional: send a demo booking confirmation SMS from the website.
    """
    data  = request.get_json(force=True, silent=True) or {}
    name  = (data.get('name') or '').strip()
    phone = (data.get('phone') or '').strip()
    slot  = (data.get('slot') or 'Tuesday at 2:00pm').strip()

    if not name or not phone:
        return jsonify({'error': 'name and phone required'}), 400

    try:
        to = clean_phone(phone)
    except Exception:
        return jsonify({'error': 'invalid phone'}), 400

    message = (
        f"Hi {name}! You're confirmed for {slot}. "
        f"I'll send a reminder 24 hours before. "
        f"Reply CHANGE anytime if you need to reschedule. — Everix AI"
    )

    ok = send_sms(to, message)
    return jsonify({'success': True, 'sms_sent': ok})


# ── RUN ───────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
