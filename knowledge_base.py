"""
Summit Legal Partners — FAQ Knowledge Base
-------------------------------------------
Used by the SMS/WhatsApp bot and AI Receptionist to answer common questions.

Practice areas: Personal Injury, Family Law, Real Estate, Corporate &
Commercial, Wills & Estates, Criminal Defence.

All consultations start with a free 30-minute intake call booked via Calendly.
"""

BUSINESS_INFO = {
    'name':     'Summit Legal Partners',
    'address':  '100 King Street West, Suite 5700, Toronto, ON M5X 1C7',
    'phone':    '(416) 362-0100',
    'email':    'info@summitlegalpartners.ca',
    'website':  'https://summitlegalpartners.ca',
    'calendly': 'https://calendly.com/everixautomation/free-ai-gap-analysis',
    'hours': {
        'Monday':    '9:00am – 5:00pm',
        'Tuesday':   '9:00am – 5:00pm',
        'Wednesday': '9:00am – 5:00pm',
        'Thursday':  '9:00am – 5:00pm',
        'Friday':    '9:00am – 5:00pm',
        'Saturday':  'Closed',
        'Sunday':    'Closed',
    },
    'emergency_line': '(416) 362-0100',
}

# ── FAQ ENTRIES ───────────────────────────────────────────────────────────
FAQ_ENTRIES = [

    # ── HOURS ────────────────────────────────────────────────────────────
    {
        'keywords': ['hours', 'open', 'close', 'closing', 'opening', 'when are you', 'what time'],
        'answer': (
            "Summit Legal Partners office hours:\n"
            "  Mon–Fri: 9:00am – 5:00pm\n"
            "  Sat–Sun: Closed\n\n"
            "Need help outside business hours? Our AI intake line is available 24/7. "
            "Text BOOK to schedule a free consultation, or call (416) 362-0100."
        ),
    },

    # ── LOCATION / TRANSIT ───────────────────────────────────────────────
    {
        'keywords': ['address', 'location', 'where', 'directions', 'parking', 'transit', 'subway'],
        'answer': (
            "We're located in the heart of Toronto's financial district:\n\n"
            "  Summit Legal Partners\n"
            "  100 King Street West, Suite 5700\n"
            "  Toronto, ON M5X 1C7\n\n"
            "Transit: King Station (Line 1) — 2-min walk west on King St.\n"
            "Parking: Underground at 100 King St W or nearby Green P lots on Adelaide.\n"
            "Virtual consultations available if preferred."
        ),
    },

    # ── FREE CONSULTATION ─────────────────────────────────────────────────
    {
        'keywords': ['free consultation', 'free call', 'cost to speak', 'initial consultation', 'first call',
                     'no cost', 'free meeting', 'speak to a lawyer'],
        'answer': (
            "Yes — your first consultation with Summit Legal Partners is free.\n\n"
            "It's a 30-minute intake call where we:\n"
            "  ✓ Review the details of your situation\n"
            "  ✓ Confirm whether we can help\n"
            "  ✓ Explain your legal options clearly\n"
            "  ✓ Outline next steps and fees if you proceed\n\n"
            "No obligation. No pressure. Text BOOK to schedule yours, or call (416) 362-0100."
        ),
    },

    # ── PRACTICE AREAS / SERVICES ─────────────────────────────────────────
    {
        'keywords': ['services', 'practice areas', 'what do you do', 'what do you handle',
                     'areas of law', 'types of cases', 'specialize'],
        'answer': (
            "Summit Legal Partners handles:\n\n"
            "  ⚖️  Personal Injury (slip & fall, MVA, disability)\n"
            "  👨‍👩‍👧  Family Law (divorce, custody, support, separation)\n"
            "  🏢  Real Estate Law (purchases, sales, refinancing)\n"
            "  💼  Corporate & Commercial (contracts, incorporations, disputes)\n"
            "  📋  Wills & Estates (wills, powers of attorney, probate)\n"
            "  🛡️  Criminal Defence (charges, bail hearings, trials)\n\n"
            "Not sure if your situation fits? Text BOOK — we'll figure it out on the call."
        ),
    },

    # ── PERSONAL INJURY ───────────────────────────────────────────────────
    {
        'keywords': ['injury', 'accident', 'car accident', 'slip and fall', 'slip & fall',
                     'mva', 'motor vehicle', 'disability', 'ltd', 'hurt', 'injured'],
        'answer': (
            "We handle personal injury claims across Ontario, including:\n\n"
            "  • Motor vehicle accidents (car, truck, motorcycle)\n"
            "  • Slip and fall / premises liability\n"
            "  • Long-term disability (LTD) denials\n"
            "  • Catastrophic injury claims\n\n"
            "Personal injury cases are handled on a contingency fee basis — "
            "you pay nothing unless we win. Text BOOK for your free 30-min consultation."
        ),
    },

    # ── FAMILY LAW ────────────────────────────────────────────────────────
    {
        'keywords': ['divorce', 'separation', 'custody', 'child support', 'spousal support',
                     'family law', 'matrimonial', 'common law', 'parenting'],
        'answer': (
            "Our family law team handles:\n\n"
            "  • Separation agreements\n"
            "  • Divorce proceedings\n"
            "  • Child custody and access\n"
            "  • Child and spousal support\n"
            "  • Property division and equalization\n"
            "  • Restraining orders\n\n"
            "We know this is a difficult time. We'll guide you clearly and protect your interests. "
            "Text BOOK for a free 30-minute consultation."
        ),
    },

    # ── REAL ESTATE ───────────────────────────────────────────────────────
    {
        'keywords': ['real estate', 'house', 'condo', 'buying', 'selling', 'purchase',
                     'closing', 'mortgage', 'refinance', 'title'],
        'answer': (
            "We handle residential and commercial real estate transactions:\n\n"
            "  • Purchase and sale closings\n"
            "  • Title transfer and review\n"
            "  • Mortgage refinancing\n"
            "  • Commercial leases\n"
            "  • Condominium law\n\n"
            "Our fixed-fee real estate services are straightforward and fully transparent. "
            "Call (416) 362-0100 or text BOOK to get a quote."
        ),
    },

    # ── WILLS & ESTATES ───────────────────────────────────────────────────
    {
        'keywords': ['will', 'estate', 'power of attorney', 'poa', 'probate', 'executor',
                     'beneficiary', 'inheritance', 'trust'],
        'answer': (
            "Our Wills & Estates team helps with:\n\n"
            "  • Drafting and updating wills\n"
            "  • Powers of attorney (property and personal care)\n"
            "  • Estate administration and probate\n"
            "  • Executor assistance\n"
            "  • Estate litigation\n\n"
            "Getting your affairs in order is one of the most important things you can do. "
            "Text BOOK for a free consultation — we make the process simple."
        ),
    },

    # ── CRIMINAL DEFENCE ─────────────────────────────────────────────────
    {
        'keywords': ['criminal', 'charged', 'arrest', 'dui', 'impaired', 'assault',
                     'theft', 'fraud', 'bail', 'court', 'police'],
        'answer': (
            "🚨 Facing criminal charges? You need a lawyer immediately.\n\n"
            "Summit Legal Partners handles:\n"
            "  • Bail hearings\n"
            "  • DUI / impaired driving\n"
            "  • Assault and weapons charges\n"
            "  • Theft, fraud, and white-collar crime\n"
            "  • Drug offences\n"
            "  • Appeals\n\n"
            "Call (416) 362-0100 right now or text URGENT. We respond to criminal matters 24/7."
        ),
    },

    # ── FEES / PRICING ────────────────────────────────────────────────────
    {
        'keywords': ['cost', 'price', 'how much', 'fee', 'pricing', 'billing', 'hourly',
                     'contingency', 'flat fee', 'retainer', 'pay', 'expensive'],
        'answer': (
            "Our fee structure depends on the type of matter:\n\n"
            "  ⚖️  Personal Injury — contingency (no fee unless we win)\n"
            "  👨‍👩‍👧  Family Law — hourly or fixed-fee packages\n"
            "  🏢  Real Estate — fixed fee (quoted upfront)\n"
            "  💼  Corporate — hourly or project-based\n"
            "  📋  Wills — fixed fee starting at $350\n"
            "  🛡️  Criminal — quoted after initial consultation\n\n"
            "Your free 30-minute consultation is always at no charge. "
            "Text BOOK or call (416) 362-0100."
        ),
    },

    # ── URGENT / EMERGENCY ────────────────────────────────────────────────
    {
        'keywords': ['urgent', 'emergency', 'asap', 'immediately', 'right now', 'today',
                     'court tomorrow', 'served today', 'just arrested'],
        'answer': (
            "🚨 Urgent legal matter? Call us immediately:\n\n"
            "  (416) 362-0100\n\n"
            "We prioritize same-day callbacks for urgent situations including:\n"
            "  • Criminal charges or arrest\n"
            "  • Restraining orders\n"
            "  • Time-sensitive court deadlines\n"
            "  • Child apprehension matters\n\n"
            "If it can't wait, call now."
        ),
    },

    # ── VIRTUAL / REMOTE ─────────────────────────────────────────────────
    {
        'keywords': ['virtual', 'online', 'video', 'zoom', 'remote', 'phone call',
                     'in person', 'come in', 'do i need to'],
        'answer': (
            "We offer both in-person and virtual consultations — your choice.\n\n"
            "  📍 In-person: 100 King St W, Suite 5700, Toronto\n"
            "  💻 Virtual: Zoom or Google Meet (we send the link)\n"
            "  📞 Phone: Available on request\n\n"
            "Most clients prefer virtual for the initial consultation. "
            "Text BOOK to get started."
        ),
    },

    # ── CANCELLATION POLICY ───────────────────────────────────────────────
    {
        'keywords': ['cancel', 'cancellation', 'reschedule', 'late cancel', 'miss', 'no show',
                     'rebook', 'change my appointment'],
        'answer': (
            "We ask for 24 hours notice to cancel or reschedule without a fee.\n\n"
            "To reschedule: text RESCHEDULE or call (416) 362-0100.\n"
            "To cancel: text CANCEL.\n\n"
            "Late cancellations (under 24 hours) for paid consultations may be subject to a $150 fee. "
            "Free initial consultations cancelled with less than 2 hours notice may result in a brief hold "
            "before rebooking."
        ),
    },

    # ── CONFIDENTIALITY ───────────────────────────────────────────────────
    {
        'keywords': ['confidential', 'private', 'privileged', 'secret', 'who will see',
                     'data', 'information safe', 'pipeda'],
        'answer': (
            "Everything you share with Summit Legal Partners is strictly confidential.\n\n"
            "  🔒 Solicitor-client privilege applies from your first contact\n"
            "  🔒 We are governed by the Law Society of Ontario's privacy rules\n"
            "  🔒 All data is handled in compliance with PIPEDA\n"
            "  🔒 We never share your information without your consent\n\n"
            "You can speak freely — nothing leaves this conversation."
        ),
    },

    # ── LAW SOCIETY / CREDENTIALS ────────────────────────────────────────
    {
        'keywords': ['licensed', 'credentials', 'bar', 'law society', 'ontario', 'regulated', 'qualified'],
        'answer': (
            "Summit Legal Partners is a fully licensed Ontario law firm regulated by the "
            "Law Society of Ontario (LSO).\n\n"
            "All our lawyers are called to the Ontario Bar and in good standing with the LSO. "
            "You can verify any lawyer's credentials at lso.ca."
        ),
    },

    # ── APPOINTMENT CONFIRMATION (handled by booking flow — do not intercept) ──
    {
        'keywords': ['confirm', 'confirmation', 'confirmed'],
        'answer': None,
    },
]

# ── LOOKUP FUNCTION ───────────────────────────────────────────────────────
def get_faq_answer(message: str) -> str | None:
    """
    Check if a message matches any FAQ keyword.
    Returns the answer string if matched, None if no match.
    Called before the state machine in sms_inbound to handle FAQ questions.
    """
    msg_upper = message.upper()
    for entry in FAQ_ENTRIES:
        if entry.get('answer') is None:
            continue
        for kw in entry.get('keywords', []):
            if kw.upper() in msg_upper:
                return entry['answer']
    return None
