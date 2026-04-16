"""
Everix Growth System — Backend (Summit Legal Partners)
=======================================================
Three systems, one backend:

  1. SPEED-TO-LEAD
     Lead submits form → instant SMS confirmation → Retell outbound qualifier
     call fires. If no answer → follow-up SMS → booking agent takes over via text.

  2. AI RECEPTIONIST (inbound calls)
     Configured in Retell.ai dashboard — handles all inbound calls.
     Books consultations, reschedules, cancels, answers FAQ — no human needed.

  3. SMS / WHATSAPP BOOKING AGENT
     Handles full consultation CRUD: book, reschedule, cancel, lookup.
     Answers FAQ from Summit Legal Partners knowledge base.
     Same webhook handles both SMS and WhatsApp.

  REMINDERS
     24-hour and 3-day consultation reminders sent automatically.
     Call /api/internal/send-reminders daily via Render cron job.

Required environment variables (set in Render dashboard):
  TWILIO_ACCOUNT_SID          twilio.com/console → Account Info
  TWILIO_AUTH_TOKEN           twilio.com/console → Account Info
  TWILIO_PHONE_NUMBER         your Twilio number e.g. +16471234567
  RETELL_API_KEY              app.retellai.com → API Keys
  RETELL_AGENT_ID             agent_ef0095051936a7d983f6bdc7de  (inbound receptionist)
  RETELL_QUALIFIER_AGENT_ID   agent_2bd18cbbc51d2207a55406d615  (outbound qualifier)
  RETELL_FROM_NUMBER          your Retell phone number e.g. +16476921660
  BUSINESS_NAME               Summit Legal Partners
  BUSINESS_PHONE              (416) 362-0100
  GOOGLE_SHEETS_ID            spreadsheet ID (optional)
  GOOGLE_CREDENTIALS_JSON     service account JSON string (optional)
  ALLOWED_ORIGIN              https://everixautomation.com
  INTERNAL_SECRET             any secret string for cron job auth
"""

import os
import json
import logging
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from knowledge_base import get_faq_answer, BUSINESS_INFO

# ── APP ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

ALLOWED_ORIGIN  = os.environ.get('ALLOWED_ORIGIN', '*')
CORS(app, origins=[ALLOWED_ORIGIN, 'http://localhost:*'])

# ── CONFIG ───────────────────────────────────────────────────────────────
TWILIO_SID      = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_TOKEN    = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_FROM     = os.environ.get('TWILIO_PHONE_NUMBER', '')
RETELL_API_KEY        = os.environ.get('RETELL_API_KEY', '')
RETELL_AGENT_ID       = os.environ.get('RETELL_AGENT_ID', '')        # inbound receptionist
RETELL_QUALIFIER_ID   = os.environ.get('RETELL_QUALIFIER_AGENT_ID', '') # outbound speed-to-lead
RETELL_FROM           = os.environ.get('RETELL_FROM_NUMBER', '')
SHEETS_ID       = os.environ.get('GOOGLE_SHEETS_ID', '')
GCREDS_JSON     = os.environ.get('GOOGLE_CREDENTIALS_JSON', '')
BUSINESS_NAME   = os.environ.get('BUSINESS_NAME', BUSINESS_INFO.get('name', 'our office'))
BUSINESS_PHONE  = os.environ.get('BUSINESS_PHONE', BUSINESS_INFO.get('phone', '647-668-4020'))
INTERNAL_SECRET = os.environ.get('INTERNAL_SECRET', '')
TIMEZONE        = ZoneInfo('America/Toronto')

twilio = Client(TWILIO_SID, TWILIO_TOKEN) if TWILIO_SID and TWILIO_TOKEN else None

# ── STORES ───────────────────────────────────────────────────────────────
# appointments: phone → { name, datetime, service, status, booked_via }
# conv_state:  phone → { name, step, slots, chosen_slot, service, ... }
appointments = {}
conv_state   = {}

# ── GOOGLE SHEETS (optional) ─────────────────────────────────────────────
sheets_svc = None
if SHEETS_ID and GCREDS_JSON:
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        creds = Credentials.from_service_account_info(
            json.loads(GCREDS_JSON),
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        sheets_svc = build('sheets', 'v4', credentials=creds)
        logger.info('Google Sheets connected.')
    except Exception as e:
        logger.warning('Google Sheets unavailable: %s', e)

def _append_sheet(phone, appt):
    if not sheets_svc or not SHEETS_ID:
        return
    try:
        sheets_svc.spreadsheets().values().append(
            spreadsheetId=SHEETS_ID,
            range='Appointments!A:G',
            valueInputOption='RAW',
            body={'values': [[
                phone,
                appt.get('name', ''),
                appt.get('datetime', ''),
                appt.get('service', ''),
                appt.get('status', 'confirmed'),
                appt.get('booked_via', 'sms'),
                datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M'),
            ]]}
        ).execute()
    except Exception as e:
        logger.warning('Sheets append error: %s', e)

# ── AVAILABLE SLOTS ──────────────────────────────────────────────────────
def available_slots(count=4):
    """Return next N open Mon–Fri slots. Replace with Google Calendar query in production."""
    slots, d = [], datetime.now(TIMEZONE).date() + timedelta(days=1)
    booked = {a.get('datetime') for a in appointments.values()}
    while len(slots) < count:
        if d.weekday() < 5:
            for hour in [9, 10, 11, 13, 14, 15, 16]:
                label = d.strftime('%A %b %-d') + f' at {hour}:00{"am" if hour < 12 else "pm"}'
                if label not in booked:
                    slots.append(label)
                if len(slots) >= count:
                    break
        d += timedelta(days=1)
    return slots

def fmt_slots(slots):
    return '\n'.join(f'  {i+1}. {s}' for i, s in enumerate(slots))

# ── HELPERS ──────────────────────────────────────────────────────────────
def clean_phone(raw):
    digits = re.sub(r'\D', '', str(raw))
    if len(digits) == 10: return '+1' + digits
    if len(digits) == 11 and digits[0] == '1': return '+' + digits
    return '+' + digits

def is_wa(num): return str(num).startswith('whatsapp:')
def strip_wa(num): return str(num).replace('whatsapp:', '')

def send(to, body, whatsapp=False):
    if not twilio:
        logger.warning('Twilio not configured — skipping message to %s', to)
        return False
    try:
        _from = f'whatsapp:{TWILIO_FROM}' if whatsapp else TWILIO_FROM
        _to   = f'whatsapp:{to}' if whatsapp and not to.startswith('whatsapp:') else to
        msg = twilio.messages.create(to=_to, from_=_from, body=body)
        logger.info('Sent to %s | SID %s', _to, msg.sid)
        return True
    except Exception as e:
        logger.error('Twilio error → %s: %s', to, e)
        return False

def retell_call(to, meta=None):
    agent_id = RETELL_QUALIFIER_ID or RETELL_AGENT_ID  # prefer qualifier for outbound
    if not RETELL_API_KEY or not agent_id:
        logger.warning('Retell not configured — call skipped for %s', to)
        return None
    try:
        r = requests.post(
            'https://api.retellai.com/v2/create-phone-call',
            headers={'Authorization': f'Bearer {RETELL_API_KEY}', 'Content-Type': 'application/json'},
            json={
                'from_number': RETELL_FROM,
                'to_number': to,
                'agent_id': agent_id,
                'metadata': meta or {},
                'retell_llm_dynamic_variables': meta or {},
            },
            timeout=10
        )
        r.raise_for_status()
        cid = r.json().get('call_id')
        logger.info('Retell call initiated → %s | call_id %s', to, cid)
        return cid
    except Exception as e:
        logger.error('Retell error: %s', e)
        return None

def xml(resp):
    return str(resp), 200, {'Content-Type': 'text/xml'}

# ─────────────────────────────────────────────────────────────────────────
# SYSTEM 1: SPEED-TO-LEAD
# ─────────────────────────────────────────────────────────────────────────
@app.route('/', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'Everix Growth System'})


@app.route('/api/demo/speed-to-lead', methods=['POST'])
def speed_to_lead():
    """
    Triggered when a lead submits a form (website, landing page, or demo page).
    Flow:
      1. Instant SMS: "We got your request — calling you now"
      2. Retell outbound call fires immediately
      3. If no answer → Retell webhook fires → follow-up SMS + booking flow begins
    """
    data    = request.get_json(force=True, silent=True) or {}
    name    = (data.get('name') or '').strip()
    phone   = (data.get('phone') or '').strip()
    service = (data.get('service') or data.get('business') or 'an appointment').strip()

    if not name or not phone:
        return jsonify({'error': 'name and phone required'}), 400
    try:
        to = clean_phone(phone)
    except Exception:
        return jsonify({'error': 'invalid phone number'}), 400

    # Step 1 — instant SMS (kept short for Twilio trial 160-char limit)
    send(to, f"Hi {name}! {BUSINESS_NAME} here. Calling you now — reply to book if you miss us.")

    # Step 2 — Retell outbound call
    call_id = retell_call(to, {
        'lead_name': name,
        'service_requested': service,
        'business_name': BUSINESS_NAME,
        'phone_number': to,
    })

    # Step 3 — store state for no-answer follow-up
    conv_state[to] = {
        'name': name, 'service': service,
        'step': 'called', 'timestamp': datetime.now(TIMEZONE).isoformat(),
    }

    return jsonify({'success': True, 'sms_sent': True,
                    'call_initiated': call_id is not None, 'call_id': call_id})


# ─────────────────────────────────────────────────────────────────────────
# SYSTEM 1 (continued): RETELL WEBHOOKS
# ─────────────────────────────────────────────────────────────────────────
@app.route('/api/retell/webhook', methods=['POST'])
def retell_webhook():
    """
    Retell fires this when a call ends.
    Set in Retell dashboard → Webhooks:
      https://everix-demo-backend.onrender.com/api/retell/webhook

    No-answer → follow-up SMS with available slots (booking agent takes over).
    """
    data  = request.get_json(force=True, silent=True) or {}
    event = data.get('event')
    call  = data.get('call', {})

    if event != 'call_ended':
        return jsonify({'received': True})

    to_num    = call.get('to_number', '')
    reason    = call.get('disconnection_reason', '')
    duration  = call.get('duration_ms', 0) / 1000
    meta      = call.get('metadata', {})
    name      = meta.get('lead_name', 'there')
    service   = meta.get('service_requested', 'appointment')

    no_answer = (
        reason in ('no_answer', 'voicemail', 'line_not_available', 'dial_failed', 'busy')
        or (duration < 15 and reason not in ('agent_hangup',))
    )

    if no_answer and to_num:
        slots = available_slots(3)
        send(to_num, (
            f"Hi {name}! We missed you — reply 1, 2, or 3 to grab a slot:\n{fmt_slots(slots)}\n"
            f"Or reply CALL ME to try again."
        ))
        conv_state[to_num] = {
            'name': name, 'service': service,
            'step': 'slot_selection', 'slots': slots,
            'timestamp': datetime.now(TIMEZONE).isoformat(),
        }
        logger.info('No-answer follow-up sent → %s', to_num)
    else:
        logger.info('Call answered and completed → %s (%.0fs)', to_num, duration)

    return jsonify({'received': True})


@app.route('/api/retell/booking-tool', methods=['POST'])
def retell_booking_tool():
    """
    Retell custom tool — called by AI agent when it books on a live call.
    Configure in Retell → Agent → Tools → Add Custom Tool:
      URL: https://everix-demo-backend.onrender.com/api/retell/booking-tool
    Saves appointment + sends confirmation SMS.
    """
    data    = request.get_json(force=True, silent=True) or {}
    name    = data.get('name', '')
    phone   = data.get('phone', '')
    appt_dt = data.get('appointment_datetime', '')
    service = data.get('service', 'appointment')

    if not phone or not appt_dt:
        return jsonify({'success': False, 'error': 'phone and appointment_datetime required'}), 400
    try:
        to = clean_phone(phone)
    except Exception:
        return jsonify({'success': False, 'error': 'invalid phone'}), 400

    appt = {'name': name, 'datetime': appt_dt, 'service': service,
            'status': 'confirmed', 'booked_via': 'phone_call'}
    appointments[to] = appt
    _append_sheet(to, appt)

    send(to, f"Booked! {name} — {service} on {appt_dt}. Text RESCHEDULE or CANCEL anytime.")
    return jsonify({'success': True, 'appointment': appt})


# ─────────────────────────────────────────────────────────────────────────
# SYSTEM 3: SMS / WHATSAPP BOOKING AGENT
# ─────────────────────────────────────────────────────────────────────────
@app.route('/api/sms/inbound', methods=['POST'])
def sms_inbound():
    """
    Handles all inbound SMS and WhatsApp messages.
    Set BOTH webhooks in Twilio to this URL:
      SMS:       Phone Numbers → your number → Messaging webhook → POST
      WhatsApp:  Messaging → Sandbox or Business → Inbound → POST
      URL: https://everix-demo-backend.onrender.com/api/sms/inbound

    Capabilities:
      BOOK / APPOINTMENT      — start new booking flow
      RESCHEDULE / REBOOK     — reschedule existing appointment
      CANCEL                  — cancel existing appointment
      STATUS / CHECK          — look up appointment
      CALL ME                 — request callback
      [FAQ question]          — answers from knowledge base
      STOP / UNSUBSCRIBE      — opt out
    """
    raw_from = request.form.get('From', '')
    body_raw = (request.form.get('Body') or '').strip()
    body     = body_raw.upper()
    wa       = is_wa(raw_from)
    phone    = strip_wa(raw_from)

    logger.info('Inbound %s from %s: "%s"', 'WA' if wa else 'SMS', phone, body_raw[:80])

    resp  = MessagingResponse()
    state = conv_state.get(phone, {})
    step  = state.get('step', 'idle')
    name  = state.get('name') or appointments.get(phone, {}).get('name', '')
    appt  = appointments.get(phone)

    # ── GLOBAL KEYWORDS ──────────────────────────────────────────────────
    if any(k in body for k in ('STOP', 'UNSUBSCRIBE', 'QUIT', 'END')):
        conv_state.pop(phone, None)
        resp.message("You've been unsubscribed. Text START anytime to re-enable messages.")
        return xml(resp)

    if 'CALL ME' in body or body in ('CALL', 'CALL BACK', 'PHONE ME', 'RING ME'):
        resp.message(
            f"Got it{', ' + name if name else ''}! "
            f"Someone from {BUSINESS_NAME} will call you shortly. "
            f"You can also reach us at {BUSINESS_PHONE}."
        )
        return xml(resp)

    # ── FAQ CHECK (only in idle / non-critical steps) ────────────────────
    if step not in _ACTIVE_STEPS:
        faq = get_faq_answer(body_raw)
        if faq:
            resp.message(faq)
            return xml(resp)

    # ── INTENT ROUTING (override flow for clear keywords) ────────────────
    if any(k in body for k in ('BOOK', 'APPOINTMENT', 'SCHEDULE', 'NEW APPOINTMENT')) \
            and step not in _BOOKING_STEPS:
        return _do_book(phone, name, appt, wa, resp)

    if any(k in body for k in ('CANCEL',)) and step not in ('cancel_confirm',):
        return _do_cancel_start(phone, name, appt, wa, resp)

    if any(k in body for k in ('RESCHEDULE', 'REBOOK', 'CHANGE', 'MOVE MY')) \
            and step not in _RESCHEDULE_STEPS:
        return _do_reschedule_start(phone, name, appt, wa, resp)

    if any(k in body for k in ('STATUS', 'CHECK', 'LOOKUP', 'MY APPOINTMENT', 'WHEN IS', 'WHAT TIME')):
        return _do_lookup(phone, name, appt, wa, resp)

    if body in ('HI', 'HELLO', 'HEY', 'START') and step == 'idle':
        return _do_book(phone, name, appt, wa, resp)

    # ── BOOKING FLOW ─────────────────────────────────────────────────────
    if step == 'booking_name':
        n = body_raw.strip().title()
        conv_state[phone].update({'name': n, 'step': 'booking_service'})
        resp.message(
            f"Nice to meet you, {n}! What type of legal matter can we help you with?\n\n"
            f"  1. Personal Injury\n"
            f"  2. Family Law\n"
            f"  3. Real Estate\n"
            f"  4. Corporate / Commercial\n"
            f"  5. Wills & Estates\n"
            f"  6. Criminal Defence\n"
            f"  7. Other / Not sure\n\n"
            f"Reply with a number or describe your situation."
        )
        return xml(resp)

    if step == 'booking_service':
        # Map numeric shortcut to practice area label
        area_map = {
            '1': 'Personal Injury Consultation',
            '2': 'Family Law Consultation',
            '3': 'Real Estate Consultation',
            '4': 'Corporate / Commercial Consultation',
            '5': 'Wills & Estates Consultation',
            '6': 'Criminal Defence Consultation',
            '7': 'General Legal Consultation',
        }
        svc = area_map.get(body.strip(), body_raw.strip().title() + ' Consultation')
        conv_state[phone].update({'service': svc, 'step': 'booking_slot'})
        slots = available_slots(4)
        conv_state[phone]['slots'] = slots
        resp.message(f"Got it — {svc}.\n\n"
                     f"Next available 30-min consultation slots:\n{fmt_slots(slots)}\n\n"
                     f"Reply 1–{len(slots)} to pick your time.")
        return xml(resp)

    if step in ('booking_slot', 'slot_selection'):
        choice = _pick_slot(body, state.get('slots') or available_slots(4))
        if not choice:
            slots = state.get('slots') or available_slots(4)
            resp.message(f"Just reply with the number of your preferred time:\n{fmt_slots(slots)}")
            return xml(resp)
        conv_state[phone].update({'chosen_slot': choice, 'step': 'booking_confirm'})
        n   = conv_state[phone].get('name', name)
        svc = conv_state[phone].get('service', 'appointment')
        resp.message(f"Just to confirm:\n\n  Name: {n}\n  Service: {svc}\n  Time: {choice}\n\n"
                     f"Reply YES to confirm or NO to see other times.")
        return xml(resp)

    if step == 'booking_confirm':
        if body in ('YES', 'Y', 'CONFIRM', 'YEP', 'SURE', 'OK', 'YUP', '👍'):
            slot = state.get('chosen_slot', 'TBD')
            svc  = state.get('service', 'appointment')
            n    = state.get('name', name)
            appt = {'name': n, 'datetime': slot, 'service': svc,
                    'status': 'confirmed', 'booked_via': 'whatsapp' if wa else 'sms'}
            appointments[phone] = appt
            _append_sheet(phone, appt)
            conv_state[phone] = {'name': n, 'step': 'idle'}
            resp.message(
                f"✅ Booked, {n}!\n\n"
                f"  {svc} at {BUSINESS_NAME}\n"
                f"  {slot}\n\n"
                f"You'll get a reminder 3 days and 24 hours before. "
                f"Text RESCHEDULE or CANCEL anytime if your plans change."
            )
        elif body in ('NO', 'N', 'NOPE', 'DIFFERENT'):
            slots = available_slots(4)
            conv_state[phone].update({'step': 'booking_slot', 'slots': slots})
            resp.message(f"No problem! Here are the available times:\n{fmt_slots(slots)}\n\nReply 1–{len(slots)}.")
        else:
            resp.message("Reply YES to confirm your appointment, or NO to pick a different time.")
        return xml(resp)

    # ── CANCEL FLOW ──────────────────────────────────────────────────────
    if step == 'cancel_confirm':
        if body in ('YES', 'Y', 'CONFIRM'):
            if phone in appointments:
                old = appointments.pop(phone)
                n = old.get('name', name)
                conv_state[phone] = {'name': n, 'step': 'idle'}
                resp.message(
                    f"Your appointment has been cancelled. "
                    f"Text BOOK whenever you're ready to reschedule, "
                    f"or call us at {BUSINESS_PHONE}."
                )
            else:
                resp.message("No appointment found to cancel. Text BOOK to schedule one.")
        elif body in ('NO', 'N', 'KEEP', 'NOPE'):
            n    = conv_state.get(phone, {}).get('name', name)
            slot = appointments.get(phone, {}).get('datetime', 'your scheduled time')
            conv_state[phone] = {'name': n, 'step': 'idle'}
            resp.message(f"No problem — your appointment for {slot} is still confirmed. "
                         f"Text RESCHEDULE if you ever need to change the time.")
        else:
            resp.message("Reply YES to cancel your appointment, or NO to keep it.")
        return xml(resp)

    # ── RESCHEDULE FLOW ──────────────────────────────────────────────────
    if step == 'reschedule_slot':
        choice = _pick_slot(body, state.get('slots') or available_slots(4))
        if not choice:
            slots = state.get('slots') or available_slots(4)
            resp.message(f"Reply with the number for your new preferred time:\n{fmt_slots(slots)}")
            return xml(resp)
        conv_state[phone].update({'chosen_slot': choice, 'step': 'reschedule_confirm'})
        resp.message(f"Reschedule to {choice}?\n\nReply YES to confirm or NO to see other times.")
        return xml(resp)

    if step == 'reschedule_confirm':
        if body in ('YES', 'Y', 'CONFIRM'):
            new_slot = state.get('chosen_slot', 'TBD')
            n = state.get('name', name)
            if phone in appointments:
                appointments[phone].update({'datetime': new_slot, 'status': 'rescheduled'})
                _append_sheet(phone, appointments[phone])
            conv_state[phone] = {'name': n, 'step': 'idle'}
            resp.message(
                f"✅ Rescheduled!\n\n"
                f"  New time: {new_slot}\n\n"
                f"We'll send reminders 3 days and 24 hours before. "
                f"Text CANCEL anytime if needed."
            )
        elif body in ('NO', 'N'):
            slots = available_slots(4)
            conv_state[phone].update({'step': 'reschedule_slot', 'slots': slots})
            resp.message(f"Here are other available times:\n{fmt_slots(slots)}")
        else:
            resp.message("Reply YES to confirm the new time, or NO to see other options.")
        return xml(resp)

    # ── REMINDER CONFIRMATION ─────────────────────────────────────────────
    if step == 'reminder_sent' and body in ('CONFIRM', 'YES', 'Y', 'OK', '✅', '👍'):
        resp.message(f"Great, see you then! Text RESCHEDULE or CANCEL if anything changes.")
        conv_state[phone] = {'name': name, 'step': 'idle'}
        return xml(resp)

    # ── FALLBACK ─────────────────────────────────────────────────────────
    if appt and appt.get('status') == 'confirmed':
        resp.message(
            f"Hi {appt.get('name', 'there')}! Your next appointment:\n"
            f"  {appt.get('service','appointment')} at {BUSINESS_NAME}\n"
            f"  {appt.get('datetime')}\n\n"
            f"Reply:\n"
            f"  RESCHEDULE — change your time\n"
            f"  CANCEL — cancel appointment\n"
            f"  CALL ME — request a callback"
        )
    else:
        resp.message(
            f"Hi! You've reached {BUSINESS_NAME}.\n\n"
            f"Reply:\n"
            f"  BOOK — schedule a free consultation\n"
            f"  HOURS — our office hours\n"
            f"  SERVICES — areas of law we handle\n"
            f"  URGENT — for time-sensitive matters\n"
            f"  CALL ME — request a callback\n\n"
            f"Or call us directly at {BUSINESS_PHONE}"
        )
    return xml(resp)


# ── FLOW HELPERS ──────────────────────────────────────────────────────────
_BOOKING_STEPS    = {'booking_name', 'booking_service', 'booking_slot', 'booking_confirm', 'slot_selection'}
_RESCHEDULE_STEPS = {'reschedule_slot', 'reschedule_confirm'}
_ACTIVE_STEPS     = _BOOKING_STEPS | _RESCHEDULE_STEPS | {'cancel_confirm'}

def _pick_slot(body, slots):
    """Match reply to a slot — by number (1/2/3/4) or partial text."""
    if body in ('1','2','3','4'):
        idx = int(body) - 1
        if 0 <= idx < len(slots):
            return slots[idx]
    for s in slots:
        if any(word in body for word in s.upper().split() if len(word) > 3):
            return s
    return None

def _do_book(phone, name, appt, wa, resp):
    if not name:
        conv_state[phone] = {'step': 'booking_name'}
        resp.message(
            f"Hi! Welcome to {BUSINESS_NAME}. I can book your free 30-minute consultation right now.\n\n"
            f"What's your name?"
        )
    else:
        conv_state.setdefault(phone, {}).update({'step': 'booking_service', 'name': name})
        resp.message(
            f"Hi {name}! What type of legal matter can we help you with?\n\n"
            f"  1. Personal Injury\n"
            f"  2. Family Law\n"
            f"  3. Real Estate\n"
            f"  4. Corporate / Commercial\n"
            f"  5. Wills & Estates\n"
            f"  6. Criminal Defence\n"
            f"  7. Other / Not sure\n\n"
            f"Reply with a number or describe your situation."
        )
    return xml(resp)

def _do_cancel_start(phone, name, appt, wa, resp):
    if not appt:
        resp.message(f"Hi{' ' + name if name else ''}! I don't have an appointment on file for this number. "
                     f"Text BOOK to schedule one, or call {BUSINESS_PHONE}.")
    else:
        conv_state.setdefault(phone, {}).update({'step': 'cancel_confirm', 'name': name})
        resp.message(f"Are you sure you want to cancel your {appt.get('service','appointment')} "
                     f"on {appt.get('datetime')}?\n\nReply YES to cancel or NO to keep it.")
    return xml(resp)

def _do_reschedule_start(phone, name, appt, wa, resp):
    if not appt:
        resp.message(f"Hi{' ' + name if name else ''}! I don't see an appointment to reschedule. "
                     f"Text BOOK to schedule a new one.")
    else:
        slots = available_slots(4)
        conv_state.setdefault(phone, {}).update({
            'step': 'reschedule_slot', 'slots': slots, 'name': name,
            'service': appt.get('service', 'appointment')
        })
        resp.message(f"Let's reschedule your {appt.get('service','appointment')}.\n\n"
                     f"Current time: {appt.get('datetime')}\n\n"
                     f"Next available slots:\n{fmt_slots(slots)}\n\nReply 1–{len(slots)}.")
    return xml(resp)

def _do_lookup(phone, name, appt, wa, resp):
    if appt:
        resp.message(f"Hi {appt.get('name','there')}! Your appointment at {BUSINESS_NAME}:\n\n"
                     f"  Service:  {appt.get('service','appointment')}\n"
                     f"  Time:     {appt.get('datetime')}\n"
                     f"  Status:   {appt.get('status','confirmed').title()}\n\n"
                     f"Text RESCHEDULE or CANCEL to make changes.")
    else:
        resp.message(f"Hi{' ' + name if name else ''}! No appointment on file for this number. "
                     f"Text BOOK to schedule one, or call {BUSINESS_PHONE}.")
    return xml(resp)


# ─────────────────────────────────────────────────────────────────────────
# REMINDERS (3-day + 24-hour)
# ─────────────────────────────────────────────────────────────────────────
@app.route('/api/internal/send-reminders', methods=['POST'])
def send_reminders():
    """
    Sends appointment reminders:
      - 3-day reminder: "Your appointment is in 3 days"
      - 24-hour reminder: "Your appointment is tomorrow — please confirm"

    Set up as a Render Cron Job (free):
      Name:     everix-reminders
      Command:  curl -s -X POST https://everix-demo-backend.onrender.com/api/internal/send-reminders
                  -H "X-Internal-Secret: YOUR_SECRET"
      Schedule: 0 14 * * *    (runs 9am EDT = 2pm UTC, every day)
    """
    secret = request.headers.get('X-Internal-Secret', '')
    if INTERNAL_SECRET and secret != INTERNAL_SECRET:
        return jsonify({'error': 'unauthorized'}), 401

    now      = datetime.now(TIMEZONE)
    tomorrow = (now + timedelta(days=1)).strftime('%A')
    in_3days = (now + timedelta(days=3)).strftime('%A')
    sent_24h = sent_3d = 0

    for phone, appt in appointments.items():
        if appt.get('status') != 'confirmed':
            continue
        dt_str = appt.get('datetime', '')
        name   = appt.get('name', 'there')
        svc    = appt.get('service', 'appointment')

        # 24-hour reminder
        if tomorrow.lower() in dt_str.lower():
            send(phone, (
                f"Reminder {name}: {svc} TOMORROW — {dt_str}.\n"
                f"Reply CONFIRM, RESCHEDULE, or CANCEL."
            ))
            conv_state[phone] = {'name': name, 'step': 'reminder_sent'}
            sent_24h += 1

        # 3-day reminder
        elif in_3days.lower() in dt_str.lower():
            send(phone, (
                f"Heads-up {name}: {svc} in 3 days — {dt_str}.\n"
                f"Reply RESCHEDULE or CANCEL if needed."
            ))
            sent_3d += 1

    logger.info('Reminders sent — 24h: %d, 3-day: %d', sent_24h, sent_3d)
    return jsonify({'sent_24h': sent_24h, 'sent_3day': sent_3d})


# ─────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
