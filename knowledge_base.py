"""
Daisy's Dental — FAQ Knowledge Base
-------------------------------------
Used by the SMS/WhatsApp bot and AI Receptionist to answer common questions.

To customize for a different client:
  - Update BUSINESS_INFO
  - Edit or add entries in FAQ_ENTRIES
  - Each entry has: keywords (what to match), answer (what to reply)

To add this to the Retell AI agent:
  - Copy the answers into your Retell agent's knowledge base
  - Or connect this file via the /api/faq endpoint

To swap this for a different client demo:
  - Create a new knowledge_base_[client].py and import it conditionally
    based on the BUSINESS_NAME environment variable.
"""

BUSINESS_INFO = {
    'name':     "Daisy's Dental Clinic",
    'address':  '2590 Yonge Street, Toronto, ON M4P 2J3',
    'phone':    '(416) 483-2590',
    'email':    'hello@daisysdental.ca',
    'website':  'http://www.daisysdental.ca',
    'hours': {
        'Monday':    '9:00am – 5:00pm',
        'Tuesday':   '9:00am – 5:00pm',
        'Wednesday': '9:00am – 5:00pm',
        'Thursday':  '9:00am – 5:00pm',
        'Friday':    '9:00am – 5:00pm',
        'Saturday':  '11:00am – 4:00pm',
        'Sunday':    'Closed',
    },
    'emergency_line': '(416) 483-2590',
}

# ── FAQ ENTRIES ───────────────────────────────────────────────────────────
# keywords: list of strings to match against the incoming message (case-insensitive)
# answer:   the reply to send back

FAQ_ENTRIES = [

    # ── HOURS ────────────────────────────────────────────────────────────
    {
        'keywords': ['hours', 'open', 'close', 'closing', 'opening', 'when are you', 'what time'],
        'answer': (
            "Our hours at Daisy's Dental Clinic:\n"
            "  Mon–Fri:  9:00am – 5:00pm\n"
            "  Saturday: 11:00am – 4:00pm\n"
            "  Sunday:   Closed\n\n"
            "Text BOOK to schedule an appointment, or call (416) 483-2590."
        ),
    },

    # ── LOCATION / PARKING ───────────────────────────────────────────────
    {
        'keywords': ['address', 'location', 'where', 'directions', 'parking'],
        'answer': (
            "We're located at:\n"
            "  2590 Yonge Street, Toronto, ON M4P 2J3\n"
            "  (Between Eglinton and Lawrence, east side of Yonge)\n\n"
            "Parking: street parking on Yonge St, or paid lot at 2600 Yonge St next door.\n"
            "TTC: Eglinton Station (Line 1) — 5-minute walk north on Yonge."
        ),
    },

    # ── INSURANCE ────────────────────────────────────────────────────────
    {
        'keywords': ['insurance', 'coverage', 'plan', 'benefits', 'covered', 'extended health', 'sunlife', 'manulife', 'great-west'],
        'answer': (
            "We accept most major insurance plans including Sun Life, Manulife, Canada Life, Great-West, "
            "Desjardins, and Blue Cross.\n\n"
            "We offer direct billing to your insurance — you only pay the difference (if any) at the time of your visit. "
            "Bring your insurance card and we'll handle the rest.\n\n"
            "Not sure if you're covered? Call us at (416) 483-2590 and we'll check for you."
        ),
    },

    # ── NEW PATIENT ──────────────────────────────────────────────────────
    {
        'keywords': ['new patient', 'first time', 'first visit', 'never been', 'new here', 'first appointment'],
        'answer': (
            "Welcome! We love new patients.\n\n"
            "Your first visit includes:\n"
            "  ✓ Comprehensive exam\n"
            "  ✓ Full mouth X-rays\n"
            "  ✓ Cleaning (if time permits)\n"
            "  ✓ Treatment plan discussion\n\n"
            "New patient visits are typically 60–90 minutes. "
            "Please bring your insurance card and a list of any medications you're taking.\n\n"
            "Text BOOK to get started!"
        ),
    },

    # ── SERVICES ─────────────────────────────────────────────────────────
    {
        'keywords': ['services', 'what do you do', 'what do you offer', 'treatments', 'procedures'],
        'answer': (
            "We offer a full range of dental services:\n\n"
            "  🦷 Cleanings & Check-ups\n"
            "  🔬 X-rays & Exams\n"
            "  🪥 Fillings & Restorations\n"
            "  👑 Crowns & Bridges\n"
            "  🦴 Dental Implants\n"
            "  😁 Teeth Whitening\n"
            "  🔧 Root Canal Treatment\n"
            "  📋 Dentures & Partials\n"
            "  🧒 Children's Dentistry\n"
            "  🆘 Emergency Dental Care\n\n"
            "Text BOOK to schedule, or call (416) 483-2590 for more info."
        ),
    },

    # ── PRICING / COST ───────────────────────────────────────────────────
    {
        'keywords': ['cost', 'price', 'how much', 'fee', 'pricing', 'expensive', 'payment', 'pay'],
        'answer': (
            "Our fees follow the Ontario Dental Association (ODA) fee guide.\n\n"
            "Typical costs:\n"
            "  Cleaning + exam: $200–$350 (usually covered by insurance)\n"
            "  Filling: $150–$300 per tooth\n"
            "  Crown: $1,200–$1,800 per tooth\n"
            "  Whitening: $400–$600\n\n"
            "We direct-bill most insurance plans, so your out-of-pocket is often $0. "
            "We also offer payment plans for larger treatments.\n\n"
            "Call (416) 483-2590 for a specific estimate."
        ),
    },

    # ── EMERGENCY ────────────────────────────────────────────────────────
    {
        'keywords': ['emergency', 'tooth pain', 'toothache', 'broken tooth', 'chipped', 'knocked out', 'urgent', 'asap', 'swollen'],
        'answer': (
            "🚨 Dental Emergency?\n\n"
            "Call us immediately at (416) 483-2590. We hold same-day emergency slots and will get you seen as soon as possible.\n\n"
            "If you're in severe pain or have facial swelling, go to the nearest emergency room or call 911."
        ),
    },

    # ── CANCELLATION POLICY ──────────────────────────────────────────────
    {
        'keywords': ['cancel', 'cancellation', 'reschedule', 'late cancel', 'miss', 'no show'],
        'answer': (
            "We ask for 24 hours notice to cancel or reschedule without a fee.\n\n"
            "To reschedule: text RESCHEDULE or call (416) 483-2590.\n"
            "To cancel: text CANCEL.\n\n"
            "Late cancellations (under 24 hours) may be subject to a $75 fee. No-shows may be charged $100."
        ),
    },

    # ── KIDS / FAMILY ────────────────────────────────────────────────────
    {
        'keywords': ['kids', 'children', 'child', 'family', 'pediatric', 'baby', 'infant', 'toddler'],
        'answer': (
            "Yes! We're a family-friendly practice and love seeing young patients. "
            "We welcome children from age 3 and recommend their first visit around age 3 or when their first teeth appear.\n\n"
            "We make kids feel comfortable and at ease — no scary drills, just friendly care.\n\n"
            "Text BOOK to schedule a family appointment."
        ),
    },

    # ── SEDATION / ANXIETY ───────────────────────────────────────────────
    {
        'keywords': ['scared', 'nervous', 'anxiety', 'fear', 'sedation', 'laughing gas', 'nitrous', 'phobia'],
        'answer': (
            "We understand dental anxiety is very common — you're not alone!\n\n"
            "We offer:\n"
            "  • Nitrous oxide (laughing gas) for mild anxiety\n"
            "  • Oral sedation for moderate anxiety\n"
            "  • A calm, judgment-free environment\n\n"
            "Let us know when booking and we'll make sure your visit is as comfortable as possible. "
            "Call (416) 483-2590 to discuss your options."
        ),
    },

    # ── WHITENING ────────────────────────────────────────────────────────
    {
        'keywords': ['whiten', 'whitening', 'bleach', 'brighter', 'stains', 'yellow'],
        'answer': (
            "We offer professional teeth whitening:\n\n"
            "  In-office whitening: ~1 hour, results immediately\n"
            "  Take-home kit: custom trays + gel, results in 1–2 weeks\n\n"
            "Professional whitening is significantly more effective than over-the-counter products.\n\n"
            "Text BOOK to schedule a whitening consultation."
        ),
    },

    # ── IMPLANTS ─────────────────────────────────────────────────────────
    {
        'keywords': ['implant', 'implants', 'missing tooth', 'missing teeth'],
        'answer': (
            "Dental implants are the gold standard for replacing missing teeth — they look, feel, and function like natural teeth.\n\n"
            "Our implant process:\n"
            "  1. Consultation & planning\n"
            "  2. Implant placement (surgical)\n"
            "  3. Healing period (3–6 months)\n"
            "  4. Crown placement\n\n"
            "Cost: typically $3,000–$5,000 per implant. Many insurance plans cover partial costs.\n\n"
            "Text BOOK for a free consultation, or call (416) 483-2590."
        ),
    },

    # ── APPOINTMENT CONFIRMATION ─────────────────────────────────────────
    {
        'keywords': ['confirm', 'confirmation', 'confirmed'],
        'answer': None,  # Handled by booking flow — don't intercept here
    },
]

# ── LOOKUP FUNCTION ───────────────────────────────────────────────────────
def get_faq_answer(message: str) -> str | None:
    """
    Check if a message matches any FAQ keyword.
    Returns the answer string if matched, None if no match.
    Call this before the state machine in sms_inbound to handle FAQ questions.
    """
    msg_upper = message.upper()
    for entry in FAQ_ENTRIES:
        if entry.get('answer') is None:
            continue
        for kw in entry.get('keywords', []):
            if kw.upper() in msg_upper:
                return entry['answer']
    return None
