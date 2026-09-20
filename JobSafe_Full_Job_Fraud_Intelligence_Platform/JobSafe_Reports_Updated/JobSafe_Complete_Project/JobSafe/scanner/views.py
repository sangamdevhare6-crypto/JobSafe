import json
import re

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .models import JobCheck, CompanyCheck


def normalize_text(text):
    text = str(text or "").lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def analyze(text, url=""):

    t = normalize_text(f"{text} {url}")

    flags = []
    score = 5

    patterns = [

        (
            [
                "registration fee",
                "registration fees",
                "registration charge",
                "joining fee",
                "joining charges",
                "application fee",
                "application charges",
                "processing fee",
                "processing charges",
                "training fee",
                "training charges",
                "security deposit",
                "refundable deposit",
                "pay first",
                "pay before joining",
                "pay to get job",
                "pay to get internship"
            ],
            35,
            "Payment or registration fee requested"
        ),

        (
            [
                "deposit money",
                "send money",
                "transfer money",
                "pay money",
                "make a payment",
                "payment required",
                "pay rs",
                "pay ₹",
                "pay inr",
                "upi payment",
                "send payment"
            ],
            30,
            "Money transfer or payment requirement detected"
        ),

        (
            [
                "gmail.com",
                "yahoo.com",
                "outlook.com",
                "hotmail.com",
                "protonmail.com",
                "rediffmail.com"
            ],
            15,
            "Personal or non-corporate email domain detected"
        ),

        (
            [
                "whatsapp only",
                "whatsapp me",
                "contact on whatsapp",
                "contact us on whatsapp",
                "message on whatsapp",
                "telegram only",
                "telegram me",
                "contact on telegram",
                "contact us on telegram"
            ],
            18,
            "Off-platform messaging pressure detected"
        ),

        (
            [
                "urgent",
                "immediately",
                "today only",
                "limited seats",
                "limited vacancies",
                "act now",
                "apply now",
                "within 24 hours",
                "last chance",
                "hurry",
                "offer expires"
            ],
            12,
            "Urgency or pressure language detected"
        ),

        (
            [
                "guaranteed job",
                "guaranteed internship",
                "guaranteed placement",
                "100% placement",
                "100% job guarantee",
                "job guaranteed",
                "easy money",
                "quick money",
                "earn money easily",
                "work from home guaranteed",
                "fixed income guaranteed"
            ],
            25,
            "Unrealistic job or income promise detected"
        ),

        (
            [
                "no interview",
                "without interview",
                "no interview required",
                "direct selection",
                "direct joining",
                "instant joining",
                "instant job",
                "selected without interview"
            ],
            18,
            "Unusual or unrealistic hiring claim detected"
        ),

        (
            [
                "otp",
                "one time password",
                "upi pin",
                "bank password",
                "net banking password",
                "atm pin",
                "cvv",
                "card details",
                "credit card number",
                "debit card number",
                "verification code",
                "login password"
            ],
            40,
            "Sensitive credential or banking information requested"
        ),

        (
            [
                "crypto",
                "bitcoin",
                "cryptocurrency",
                "gift card",
                "usdt",
                "wallet address"
            ],
            25,
            "Suspicious cryptocurrency or gift-card request detected"
        ),

        (
            [
                "lottery",
                "prize",
                "reward",
                "claim your money",
                "claim reward",
                "you have won",
                "winner",
                "lucky winner"
            ],
            20,
            "Suspicious reward or prize language detected"
        ),

        (
            [
                "registration link",
                "verify your account",
                "verify immediately",
                "click this link",
                "click the link",
                "download this app",
                "install this app",
                "download apk"
            ],
            15,
            "Suspicious verification or external-link instruction detected"
        ),

        (
            [
                "send your documents",
                "send documents immediately",
                "send aadhaar",
                "aadhaar card",
                "pan card",
                "passport copy",
                "bank statement",
                "bank account details"
            ],
            15,
            "Sensitive personal or financial document request detected"
        ),

        (
            [
                "referral fee",
                "membership fee",
                "membership charge",
                "course fee",
                "certificate fee",
                "verification fee",
                "background verification fee"
            ],
            25,
            "Employment-related fee or charge detected"
        ),

        (
            [
                "paytm",
                "phonepe",
                "google pay",
                "gpay",
                "upi id"
            ],
            10,
            "Payment-platform information detected"
        )
    ]

    for words, points, reason in patterns:

        if any(word in t for word in words):

            score += points

            flags.append(reason)

    url_text = normalize_text(url)

    if url_text:

        suspicious_url_patterns = [
            "bit.ly",
            "tinyurl.com",
            "t.co/",
            "cutt.ly",
            "is.gd",
            "shorturl.at",
            "rebrand.ly",
            "rb.gy"
        ]

        if any(
            item in url_text
            for item in suspicious_url_patterns
        ):

            score += 15

            flags.append(
                "URL shortener detected; verify the destination before applying"
            )

    if re.search(
        r"(₹|rs\.?|inr)\s?\d[\d,]*",
        t
    ):

        payment_words = [
            "pay",
            "fee",
            "charge",
            "deposit",
            "payment",
            "registration",
            "joining"
        ]

        if any(
            word in t
            for word in payment_words
        ):

            score += 20

            flags.append(
                "Specific monetary amount associated with a job-related request detected"
            )

    if (
        "whatsapp" in t
        and
        (
            "pay" in t
            or "fee" in t
            or "deposit" in t
            or "money" in t
        )
    ):

        score += 10

        flags.append(
            "Payment request combined with WhatsApp communication detected"
        )

    unique_flags = []

    for flag in flags:

        if flag not in unique_flags:
            unique_flags.append(flag)

    flags = unique_flags

    score = min(score, 99)

    if score >= 70:
        level = "High Risk"
    elif score >= 35:
        level = "Suspicious"
    else:
        level = "Safe"

    if not flags:

        flags = [
            "No major scam signals detected by the JobSafe rule engine"
        ]

    return score, level, flags


@login_required
def check_job(request):

    result = None

    if request.method == "POST":

        title = request.POST.get(
            "title",
            "Untitled Job"
        )

        company = request.POST.get(
            "company",
            ""
        )

        url = request.POST.get(
            "url",
            ""
        )

        description = request.POST.get(
            "description",
            ""
        )

        score, level, flags = analyze(
            description,
            url
        )

        obj = JobCheck.objects.create(
            user=request.user,
            title=title,
            company=company,
            url=url,
            description=description,
            risk_score=score,
            risk_level=level,
            reasons="|".join(flags)
        )

        result = {
            "obj": obj,
            "flags": flags
        }

    return render(
        request,
        "check-job.html",
        {
            "result": result
        }
    )


@login_required
@ensure_csrf_cookie
def screenshot_scanner(request):

    return render(
        request,
        "screenshot-scanner.html"
    )


@login_required
@require_POST
def analyze_screenshot(request):

    try:

        data = json.loads(
            request.body.decode("utf-8")
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError
    ):

        return JsonResponse(
            {
                "success": False,
                "error": "Invalid request data."
            },
            status=400
        )

    text = str(
        data.get(
            "text",
            ""
        )
    ).strip()

    url = str(
        data.get(
            "url",
            ""
        )
    ).strip()

    if not text:

        return JsonResponse(
            {
                "success": False,
                "error": "No text was provided for analysis."
            },
            status=400
        )

    score, level, flags = analyze(
        text,
        url
    )

    return JsonResponse(
        {
            "success": True,
            "risk_score": score,
            "risk_level": level,
            "reasons": flags,
            "extracted_text": text
        }
    )


@login_required
def company_check(request):

    result = None

    if request.method == "POST":

        company = request.POST.get(
            "company",
            "Unknown Company"
        ).strip()

        website = request.POST.get(
            "website",
            ""
        ).strip()

        domain = request.POST.get(
            "domain",
            ""
        ).strip()

        risk = 20
        status = "Verified"

        if website and not website.startswith("https://"):

            risk += 20

        if not website:

            risk += 15
            status = "Needs Review"

        free_domains = [
            "gmail",
            "yahoo",
            "outlook",
            "hotmail",
            "protonmail",
            "rediffmail"
        ]

        if any(
            item in domain.lower()
            for item in free_domains
        ):

            risk += 35
            status = "Needs Review"

        risk = min(risk, 95)

        if risk >= 60:
            status = "High Risk"

        elif risk >= 35:
            status = "Needs Review"

        CompanyCheck.objects.create(
            user=request.user,
            company=company,
            website=website,
            domain=domain,
            risk_score=risk,
            status=status
        )

        result = {
            "company": company,
            "risk": risk,
            "status": status
        }

    return render(
        request,
        "company-check.html",
        {
            "result": result
        }
    )