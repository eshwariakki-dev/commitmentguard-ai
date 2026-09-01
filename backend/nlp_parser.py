"""
Requirement extraction from natural-language buyer requests.

Tries Gemini first if GEMINI_API_KEY is set.
Falls back to a deterministic parser if Gemini is unavailable.

This module extracts what the buyer is asking for.
It does not decide whether a product satisfies the request.
commitment_guard.py performs the actual verification.
"""

import os
import re
import json
from datetime import datetime, timedelta


# ---------------------------------------------------------
# Helper: convert text numbers to integers
# ---------------------------------------------------------

NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


# ---------------------------------------------------------
# PRODUCT EXTRACTION
# ---------------------------------------------------------

def extract_product(text):
    """
    Try to identify what product the customer wants.

    This is intentionally NOT restricted to a fixed category list.
    """

    text_lower = text.lower().strip()

    # Common phrases used before the product name
    patterns = [
        r"(?:i need|i want|i am looking for|looking for|need|want|buy|purchase)\s+(?:a|an|the)?\s*(.+?)(?=\s+(?:under|below|less than|within|before|by|for|at|delivered|delivery|in)\b|$)",

        r"(?:looking for)\s+(?:a|an|the)?\s*(.+?)(?=\s+(?:under|below|less than|within|before|by|for|at|delivered|delivery|in)\b|$)",

        r"(?:give me|get me)\s+(?:a|an|the)?\s*(.+?)(?=\s+(?:under|below|less than|within|before|by|for|at|delivered|delivery|in)\b|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text_lower)

        if match:
            product = match.group(1).strip()

            # Remove unnecessary articles
            product = re.sub(
                r"^(a|an|the)\s+",
                "",
                product
            ).strip()

            if product:
                return product

    # Fallback:
    # Try to remove requirement words and keep the remaining phrase.
    cleaned = text_lower

    cleaned = re.sub(
        r"\b(i|need|want|require|looking|for|a|an|the|please|give|me)\b",
        " ",
        cleaned
    )

    cleaned = re.sub(
        r"\b(under|below|less than|within)\s*(?:₹|rs\.?|inr)?\s*\d[\d,]*",
        " ",
        cleaned
    )

    cleaned = re.sub(
        r"\b(before|by)\s+\d{1,2}(?:st|nd|rd|th)?\s+[a-z]+",
        " ",
        cleaned
    )

    cleaned = re.sub(
        r"\b(tomorrow|today|next\s+\w+|within\s+\w+\s+days?)\b",
        " ",
        cleaned
    )

    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned if cleaned else None


# ---------------------------------------------------------
# CATEGORY EXTRACTION
# ---------------------------------------------------------

def extract_category(product):
    """
    Create a simple category from the detected product.

    This does NOT restrict the product to predefined categories.
    """

    if not product:
        return "unknown"

    product_lower = product.lower().strip()

    # Basic generic grouping.
    # Unknown products are still accepted.
    category_rules = {
        "laptops": [
            "laptop",
            "notebook",
            "macbook",
            "computer"
        ],
        "headphones": [
            "headphone",
            "earbud",
            "earphone"
        ],
        "phones": [
            "phone",
            "smartphone",
            "iphone",
            "mobile"
        ],
        "televisions": [
            "television",
            "tv"
        ],
        "watches": [
            "watch",
            "smartwatch"
        ],
        "jewellery": [
            "necklace",
            "ring",
            "bracelet",
            "earring",
            "jewelry",
            "jewellery"
        ],
        "footwear": [
            "shoe",
            "shoes",
            "sandal",
            "sandals",
            "slipper",
            "boots"
        ],
        "clothing": [
            "shirt",
            "t-shirt",
            "tshirt",
            "jeans",
            "dress",
            "jacket",
            "trouser",
            "pants"
        ],
        "home_appliances": [
            "washing machine",
            "refrigerator",
            "fridge",
            "microwave",
            "mixer",
            "grinder",
            "air conditioner",
            "ac"
        ],
        "furniture": [
            "chair",
            "table",
            "sofa",
            "bed",
            "desk",
            "wardrobe"
        ],
        "bags": [
            "bag",
            "backpack",
            "luggage",
            "suitcase"
        ],
        "toys": [
            "toy",
            "lego",
            "doll"
        ],
        "sports": [
            "cricket bat",
            "football",
            "basketball",
            "badminton",
            "racket",
            "sports"
        ],
        "electronics": [
            "camera",
            "printer",
            "speaker",
            "monitor",
            "keyboard",
            "mouse",
            "tablet"
        ],
    }

    for category, keywords in category_rules.items():
        for keyword in keywords:
            if keyword in product_lower:
                return category

    # If no known group exists, use the product itself
    # as the category rather than returning an unusable value.
    return product


# ---------------------------------------------------------
# BUDGET EXTRACTION
# ---------------------------------------------------------

def extract_budget(text):
    text_lower = text.lower()

    # Examples:
    # under 60000
    # below ₹60000
    # less than 60,000
    # within 5000
    # under rs 60000

    budget_match = re.search(
        r"(?:under|below|less than|within)\s*"
        r"(?:₹|rs\.?|inr)?\s*"
        r"(\d[\d,]*)",
        text_lower
    )

    if budget_match:
        return int(
            budget_match.group(1).replace(",", "")
        )

    # ₹60000
    # Rs 60000
    # INR 60000

    currency_match = re.search(
        r"(?:₹|rs\.?|inr)\s*(\d[\d,]*)",
        text_lower
    )

    if currency_match:
        return int(
            currency_match.group(1).replace(",", "")
        )

    # 60k / 1.5 lakh / 2 lakh
    k_match = re.search(
        r"(?:under|below|less than|within)\s*"
        r"(\d+(?:\.\d+)?)\s*k\b",
        text_lower
    )

    if k_match:
        return int(float(k_match.group(1)) * 1000)

    lakh_match = re.search(
        r"(?:under|below|less than|within)\s*"
        r"(\d+(?:\.\d+)?)\s*(?:lakh|lac)\b",
        text_lower
    )

    if lakh_match:
        return int(float(lakh_match.group(1)) * 100000)

    return None


# ---------------------------------------------------------
# DATE HELPERS
# ---------------------------------------------------------

MONTHS = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}


WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def clean_ordinal(value):
    """
    Convert:
    1st -> 1
    2nd -> 2
    3rd -> 3
    15th -> 15
    """

    return int(
        re.sub(r"(st|nd|rd|th)$", "", value)
    )


def parse_specific_date(text):
    """
    Detect dates such as:

    15th August
    15 August
    August 15
    August 15th
    15/08/2026
    15-08-2026
    """

    text_lower = text.lower()
    today = datetime.now().date()

    # ---------------------------------------------
    # 15th August 2026
    # 15 August 2026
    # ---------------------------------------------

    match = re.search(
        r"\b(\d{1,2})(?:st|nd|rd|th)?\s+"
        r"([a-z]+)"
        r"(?:\s+(\d{4}))?\b",
        text_lower
    )

    if match:
        day = clean_ordinal(match.group(1))
        month_name = match.group(2)
        year = match.group(3)

        if month_name in MONTHS:
            month = MONTHS[month_name]

            if year:
                year = int(year)
            else:
                year = today.year

                # If the date already passed this year,
                # assume the next occurrence.
                try:
                    candidate = datetime(
                        year,
                        month,
                        day
                    ).date()

                    if candidate < today:
                        year += 1

                except ValueError:
                    return None

            try:
                return datetime(
                    year,
                    month,
                    day
                ).date()

            except ValueError:
                return None

    # ---------------------------------------------
    # August 15th
    # August 15
    # August 15 2026
    # ---------------------------------------------

    match = re.search(
        r"\b([a-z]+)\s+"
        r"(\d{1,2})(?:st|nd|rd|th)?"
        r"(?:\s+(\d{4}))?\b",
        text_lower
    )

    if match:
        month_name = match.group(1)
        day = int(match.group(2))
        year = match.group(3)

        if month_name in MONTHS:
            month = MONTHS[month_name]

            if year:
                year = int(year)
            else:
                year = today.year

                try:
                    candidate = datetime(
                        year,
                        month,
                        day
                    ).date()

                    if candidate < today:
                        year += 1

                except ValueError:
                    return None

            try:
                return datetime(
                    year,
                    month,
                    day
                ).date()

            except ValueError:
                return None

    # ---------------------------------------------
    # 15/08/2026 or 15-08-2026
    # ---------------------------------------------

    match = re.search(
        r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{4}))?\b",
        text_lower
    )

    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = (
            int(match.group(3))
            if match.group(3)
            else today.year
        )

        try:
            candidate = datetime(
                year,
                month,
                day
            ).date()

            if not match.group(3) and candidate < today:
                candidate = datetime(
                    year + 1,
                    month,
                    day
                ).date()

            return candidate

        except ValueError:
            return None

    return None


def parse_delivery_requirement(text):
    """
    Detect many delivery formats.

    Examples:

    tomorrow
    today
    within 3 days
    in 5 days
    before 15th August
    by 20 September
    next Monday
    by Friday
    next week
    """

    text_lower = text.lower().strip()
    today = datetime.now().date()

    deadline = None
    condition = None

    # ---------------------------------------------
    # TODAY
    # ---------------------------------------------

    if re.search(r"\btoday\b", text_lower):
        deadline = today
        condition = "by"

    # ---------------------------------------------
    # TOMORROW
    # ---------------------------------------------

    elif re.search(r"\btomorrow\b", text_lower):
        deadline = today + timedelta(days=1)
        condition = "by"

    # ---------------------------------------------
    # IN X DAYS
    # ---------------------------------------------

    else:
        match = re.search(
            r"\bin\s+(\d+)\s+days?\b",
            text_lower
        )

        if match:
            days = int(match.group(1))
            deadline = today + timedelta(days=days)
            condition = "within"

    # ---------------------------------------------
    # WITHIN X DAYS
    # ---------------------------------------------

    if deadline is None:
        match = re.search(
            r"\bwithin\s+(\d+)\s+days?\b",
            text_lower
        )

        if match:
            days = int(match.group(1))
            deadline = today + timedelta(days=days)
            condition = "within"

    # ---------------------------------------------
    # IN ONE/TWO/THREE DAYS
    # ---------------------------------------------

    if deadline is None:
        match = re.search(
            r"\bin\s+(one|two|three|four|five|six|seven|eight|nine|ten)\s+days?\b",
            text_lower
        )

        if match:
            days = NUMBER_WORDS[match.group(1)]
            deadline = today + timedelta(days=days)
            condition = "within"

    # ---------------------------------------------
    # WITHIN A WEEK
    # ---------------------------------------------

    if deadline is None and "within a week" in text_lower:
        deadline = today + timedelta(days=7)
        condition = "within"

    # ---------------------------------------------
    # NEXT WEEK
    # ---------------------------------------------

    if deadline is None and re.search(
        r"\bnext\s+week\b",
        text_lower
    ):
        deadline = today + timedelta(days=7)
        condition = "by"

    # ---------------------------------------------
    # NEXT MONDAY / NEXT FRIDAY etc.
    # ---------------------------------------------

    if deadline is None:
        match = re.search(
            r"\bnext\s+"
            r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
            text_lower
        )

        if match:
            target_day = WEEKDAYS[match.group(1)]
            current_day = today.weekday()

            days_ahead = (
                target_day - current_day
            ) % 7

            if days_ahead == 0:
                days_ahead = 7

            deadline = today + timedelta(
                days=days_ahead
            )

            condition = "by"

    # ---------------------------------------------
    # BY FRIDAY / BEFORE MONDAY
    # ---------------------------------------------

    if deadline is None:
        match = re.search(
            r"\b(?:by|before)\s+"
            r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
            text_lower
        )

        if match:
            target_day = WEEKDAYS[match.group(1)]
            current_day = today.weekday()

            days_ahead = (
                target_day - current_day
            ) % 7

            if days_ahead == 0:
                days_ahead = 7

            deadline = today + timedelta(
                days=days_ahead
            )

            condition = (
                "before"
                if "before" in match.group(0)
                else "by"
            )

    # ---------------------------------------------
    # SPECIFIC DATE
    # ---------------------------------------------

    if deadline is None:
        specific_date = parse_specific_date(text)

        if specific_date:
            deadline = specific_date

            if re.search(
                r"\bbefore\b",
                text_lower
            ):
                condition = "before"
            else:
                condition = "by"

    # ---------------------------------------------
    # RETURN
    # ---------------------------------------------

    if deadline is None:
        return {
            "max_delivery_days": None,
            "delivery_deadline": None,
            "delivery_condition": None,
        }

    max_delivery_days = (
        deadline - today
    ).days

    return {
        "max_delivery_days": max_delivery_days,
        "delivery_deadline": deadline.isoformat(),
        "delivery_condition": condition,
    }


# ---------------------------------------------------------
# FALLBACK PARSER
# ---------------------------------------------------------

def fallback_parse(text):
    """
    Extract requirements without using an AI model.
    """

    product = extract_product(text)
    category = extract_category(product)
    max_budget = extract_budget(text)
    delivery = parse_delivery_requirement(text)

    return {
        "product": product,
        "category": category,
        "max_budget": max_budget,

        "max_delivery_days": delivery[
            "max_delivery_days"
        ],

        "delivery_deadline": delivery[
            "delivery_deadline"
        ],

        "delivery_condition": delivery[
            "delivery_condition"
        ],

        "source": "fallback_parser",
    }


# ---------------------------------------------------------
# GEMINI PARSER
# ---------------------------------------------------------

def extract_requirements(text):
    """
    Extract buyer requirements using Gemini.

    If Gemini is unavailable or fails,
    automatically use the fallback parser.
    """

    api_key = os.environ.get("GEMINI_API_KEY")

    # No Gemini API key
    if not api_key:
        return fallback_parse(text)

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(
            "gemini-1.5-flash"
        )

        today = datetime.now().date().isoformat()

        prompt = f"""
You are a shopping requirement extraction system.

Extract the customer's shopping requirements from the
request below.

Return STRICT JSON only.
Do not return markdown.
Do not return explanations.

Today's date is {today}.

Important rules:

1. The customer may request ANY product.
2. Do not restrict products to a predefined category list.
3. Extract the actual product the customer wants.
4. Identify a useful general category if possible.
5. Keep product names such as:
   - Samsung washing machine
   - gold necklace
   - gaming laptop
   - cricket bat
   - running shoes
   - camera
6. Extract the maximum budget in INR.
7. Understand different budget expressions:
   - under 60000
   - below ₹60000
   - less than 60,000
   - within 60k
   - under 1 lakh
8. Understand delivery requirements:
   - tomorrow
   - today
   - within 3 days
   - in 5 days
   - before 15th August
   - by 20 September
   - next Monday
   - by Friday
9. Convert a specific delivery date into ISO format YYYY-MM-DD.
10. max_delivery_days should represent the number of days
    from today's date to the delivery deadline.
11. If the customer does not mention delivery, use null.
12. If the customer does not mention a budget, use null.
13. Never invent a product, price, or delivery requirement.

Required JSON fields:

{{
    "product": "string or null",
    "category": "string or null",
    "max_budget": number or null,
    "max_delivery_days": number or null,
    "delivery_deadline": "YYYY-MM-DD or null",
    "delivery_condition": "before, by, within, or null"
}}

Buyer request:

"{text}"
"""

        response = model.generate_content(prompt)

        raw = response.text.strip()

        # Remove markdown code fences if Gemini adds them
        raw = re.sub(
            r"^```json\s*",
            "",
            raw,
            flags=re.IGNORECASE
        )

        raw = re.sub(
            r"\s*```$",
            "",
            raw
        )

        parsed = json.loads(raw)

        # -------------------------------------------------
        # Ensure fields always exist
        # -------------------------------------------------

        parsed.setdefault(
            "product",
            None
        )

        parsed.setdefault(
            "category",
            None
        )

        parsed.setdefault(
            "max_budget",
            None
        )

        parsed.setdefault(
            "max_delivery_days",
            None
        )

        parsed.setdefault(
            "delivery_deadline",
            None
        )

        parsed.setdefault(
            "delivery_condition",
            None
        )

        # -------------------------------------------------
        # If Gemini misses something, use fallback values
        # -------------------------------------------------

        fallback = fallback_parse(text)

        if not parsed.get("product"):
            parsed["product"] = fallback["product"]

        if not parsed.get("category"):
            parsed["category"] = fallback["category"]

        if parsed.get("max_budget") is None:
            parsed["max_budget"] = fallback["max_budget"]

        if parsed.get("delivery_deadline") is None:
            parsed["delivery_deadline"] = fallback[
                "delivery_deadline"
            ]

        if parsed.get("delivery_condition") is None:
            parsed["delivery_condition"] = fallback[
                "delivery_condition"
            ]

        if parsed.get("max_delivery_days") is None:
            parsed["max_delivery_days"] = fallback[
                "max_delivery_days"
            ]

        parsed["source"] = "gemini"

        return parsed

    except Exception:
        result = fallback_parse(text)

        result["source"] = (
            "fallback_parser (gemini_unavailable)"
        )

        return result