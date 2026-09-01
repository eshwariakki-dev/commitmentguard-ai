from datetime import datetime


# =========================================================
# AUDIT TRAIL
# =========================================================

def build_audit_entry(step_number, action, detail):
    return {
        "step": step_number,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "action": action,
        "detail": detail,
    }


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text):
    """
    Normalize text so product matching works with
    different capitalization and punctuation.
    """

    if not text:
        return ""

    text = str(text).lower()

    replacements = {
        "-": " ",
        "_": " ",
        "/": " ",
        ",": " ",
        ".": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return " ".join(text.split())


def tokenize(text):
    """
    Convert text into useful words.
    """

    text = normalize_text(text)

    if not text:
        return set()

    return set(text.split())


# =========================================================
# PRODUCT MATCHING
# =========================================================

def product_matches_request(product, requirements):
    """
    Determine whether a catalog product matches the customer's
    requested product.

    Matching uses:
    1. Product name
    2. Product category
    3. Description
    4. Attributes
    """

    requested_product = normalize_text(
        requirements.get("product")
    )

    requested_category = normalize_text(
        requirements.get("category")
    )

    if not requested_product and not requested_category:
        return False

    product_name = normalize_text(
        product.get("name", "")
    )

    product_category = normalize_text(
        product.get("category", "")
    )

    product_description = normalize_text(
        product.get("description", "")
    )

    product_attributes = normalize_text(
        " ".join(product.get("attributes", []))
    )

    searchable_text = " ".join([
        product_name,
        product_category,
        product_description,
        product_attributes,
    ])

    # -----------------------------------------------------
    # Strongest match: requested product phrase
    # -----------------------------------------------------

    if requested_product:
        if requested_product in searchable_text:
            return True

    # -----------------------------------------------------
    # Match important product words
    # -----------------------------------------------------

    if requested_product:
        requested_words = tokenize(requested_product)

        # Remove generic words
        ignored_words = {
            "a",
            "an",
            "the",
            "i",
            "need",
            "want",
            "looking",
            "for",
            "please",
            "give",
            "me",
            "buy",
            "purchase",
        }

        requested_words -= ignored_words

        searchable_words = tokenize(searchable_text)

        if requested_words:
            matched_words = (
                requested_words & searchable_words
            )

            # Require meaningful product-word overlap.
            #
            # Example:
            # "laptop" -> laptop
            # "necklace" -> necklace
            # "gaming laptop" -> laptop + gaming
            if len(requested_words) == 1:
                if len(matched_words) >= 1:
                    return True
            else:
                match_ratio = (
                    len(matched_words) /
                    len(requested_words)
                )

                if match_ratio >= 0.5:
                    return True

    # -----------------------------------------------------
    # Category match
    # -----------------------------------------------------

    if requested_category:
        if requested_category == product_category:
            return True

        if requested_category in product_category:
            return True

    return False


def calculate_match_score(product, requirements):
    """
    Give a score to matching products.

    Higher score means a better product match.
    """

    requested_product = normalize_text(
        requirements.get("product")
    )

    requested_category = normalize_text(
        requirements.get("category")
    )

    product_name = normalize_text(
        product.get("name", "")
    )

    product_category = normalize_text(
        product.get("category", "")
    )

    product_description = normalize_text(
        product.get("description", "")
    )

    product_attributes = normalize_text(
        " ".join(product.get("attributes", []))
    )

    searchable_text = " ".join([
        product_name,
        product_category,
        product_description,
        product_attributes,
    ])

    score = 0

    # Exact product phrase
    if requested_product:
        if requested_product in product_name:
            score += 100

        elif requested_product in searchable_text:
            score += 70

    # Product word overlap
    requested_words = tokenize(requested_product)
    searchable_words = tokenize(searchable_text)

    if requested_words:
        overlap = (
            requested_words & searchable_words
        )

        score += len(overlap) * 20

    # Exact category
    if requested_category:
        if requested_category == product_category:
            score += 50

        elif requested_category in product_category:
            score += 30

    return score


def find_matching_products(catalog, requirements):
    """
    Search the complete catalog.

    The search is NOT restricted to a predefined category list.
    """

    matches = []

    for product in catalog:

        if product_matches_request(
            product,
            requirements
        ):
            score = calculate_match_score(
                product,
                requirements
            )

            matches.append({
                "product": product,
                "score": score,
            })

    # Highest matching score first
    matches.sort(
        key=lambda item: (
            -item["score"],
            item["product"].get("price", float("inf"))
        )
    )

    return [
        item["product"]
        for item in matches
    ]


# =========================================================
# VERIFICATION
# =========================================================

def verify_commitment(product, requirements):

    checks = []
    all_passed = True

    # -----------------------------------------------------
    # 1. PRODUCT MATCH
    # -----------------------------------------------------

    product_match = product_matches_request(
        product,
        requirements
    )

    checks.append({
        "requirement": "Product match",
        "passed": product_match,
        "detail": (
            f"{product['name']} matches the requested product"
            if product_match
            else f"{product['name']} does not match the requested product"
        ),
    })

    if not product_match:
        all_passed = False

    # -----------------------------------------------------
    # 2. STOCK CHECK
    # -----------------------------------------------------

    stock = product.get("stock", 0)

    in_stock = stock > 0

    checks.append({
        "requirement": "Stock availability",
        "passed": in_stock,
        "detail": (
            f"{stock} units available"
            if in_stock
            else "Out of stock (0 units)"
        ),
    })

    if not in_stock:
        all_passed = False

    # -----------------------------------------------------
    # 3. BUDGET CHECK
    # -----------------------------------------------------

    max_budget = requirements.get(
        "max_budget"
    )

    if max_budget is not None:

        price = product.get(
            "price",
            float("inf")
        )

        within_budget = price <= max_budget

        checks.append({
            "requirement": "Budget requirement",
            "passed": within_budget,
            "detail": (
                f"₹{price} is within ₹{max_budget} budget"
                if within_budget
                else f"₹{price} exceeds ₹{max_budget} budget"
            ),
        })

        if not within_budget:
            all_passed = False

    # -----------------------------------------------------
    # 4. DELIVERY CHECK
    # -----------------------------------------------------

    max_delivery_days = requirements.get(
        "max_delivery_days"
    )

    if max_delivery_days is not None:

        delivery_days = product.get(
            "delivery_days",
            999999
        )

        deliverable = (
            delivery_days <= max_delivery_days
        )

        checks.append({
            "requirement": "Delivery commitment",
            "passed": deliverable,
            "detail": (
                f"Delivers in {delivery_days} day(s), "
                f"meets the {max_delivery_days}-day requirement"
                if deliverable
                else
                f"Delivers in {delivery_days} day(s), "
                f"exceeds the {max_delivery_days}-day requirement"
            ),
        })

        if not deliverable:
            all_passed = False

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    return {
        "product": product,
        "status": (
            "VERIFIED"
            if all_passed
            else "BLOCKED"
        ),
        "checks": checks,
    }


# =========================================================
# FIND ALTERNATIVE
# =========================================================

def find_alternative(
    catalog,
    failed_product,
    requirements
):
    """
    Search the complete catalog for another product
    matching the customer's request and satisfying
    all requirements.
    """

    candidates = []

    for product in catalog:

        if product.get("id") == failed_product.get("id"):
            continue

        # The alternative must still match the
        # customer's requested product.
        if not product_matches_request(
            product,
            requirements
        ):
            continue

        verification = verify_commitment(
            product,
            requirements
        )

        if verification["status"] == "VERIFIED":

            score = calculate_match_score(
                product,
                requirements
            )

            candidates.append({
                "product": product,
                "verification": verification,
                "score": score,
            })

    if not candidates:
        return None

    # Best product match first.
    # If equally matched, choose lower price.
    candidates.sort(
        key=lambda item: (
            -item["score"],
            item["product"].get(
                "price",
                float("inf")
            )
        )
    )

    return candidates[0]


# =========================================================
# MAIN VERIFICATION FLOW
# =========================================================

def run_verification_flow(
    catalog,
    requirements
):

    audit = []
    step = 1

    # -----------------------------------------------------
    # STEP 1: REQUEST RECEIVED
    # -----------------------------------------------------

    audit.append(
        build_audit_entry(
            step,
            "Buyer request received",
            f"Parsed requirements: {requirements}"
        )
    )

    step += 1

    # -----------------------------------------------------
    # STEP 2: SEARCH CATALOG
    # -----------------------------------------------------

    matches = find_matching_products(
        catalog,
        requirements
    )

    requested_product = (
        requirements.get("product")
        or requirements.get("category")
        or "unknown product"
    )

    audit.append(
        build_audit_entry(
            step,
            "Products searched",
            f"Searching the complete catalog for '{requested_product}'. "
            f"Found {len(matches)} matching product(s)."
        )
    )

    step += 1

    # -----------------------------------------------------
    # NO PRODUCT MATCH
    # -----------------------------------------------------

    if not matches:

        audit.append(
            build_audit_entry(
                step,
                "No products found",
                f"No catalog product matches '{requested_product}'."
            )
        )

        return {
            "requirements": requirements,
            "proposed_product": None,
            "verification": None,
            "alternative": None,
            "final_status": "NO_MATCH",
            "message": (
                f"No product matching "
                f"'{requested_product}' was found "
                f"in the catalog."
            ),
            "audit_trail": audit,
        }

    # -----------------------------------------------------
    # STEP 3: CHECK MATCHES
    # -----------------------------------------------------

    verified_products = []
    blocked_products = []

    for product in matches:

        verification = verify_commitment(
            product,
            requirements
        )

        if verification["status"] == "VERIFIED":

            verified_products.append({
                "product": product,
                "verification": verification,
            })

        else:

            blocked_products.append({
                "product": product,
                "verification": verification,
            })

    # -----------------------------------------------------
    # STEP 4: IF A VERIFIED PRODUCT EXISTS
    # -----------------------------------------------------

    if verified_products:

        # Best matching product first.
        # Lower price breaks ties.
        verified_products.sort(
            key=lambda item: (
                -calculate_match_score(
                    item["product"],
                    requirements
                ),
                item["product"].get(
                    "price",
                    float("inf")
                )
            )
        )

        selected = verified_products[0]

        proposed = selected["product"]
        verification = selected["verification"]

        audit.append(
            build_audit_entry(
                step,
                "Verified product selected",
                f"{proposed['name']} "
                f"(₹{proposed['price']}) satisfies all requirements."
            )
        )

        step += 1

        for check in verification["checks"]:

            audit.append(
                build_audit_entry(
                    step,
                    (
                        f"{check['requirement']} "
                        f"{'verified' if check['passed'] else 'FAILED'}"
                    ),
                    check["detail"]
                )
            )

            step += 1

        audit.append(
            build_audit_entry(
                step,
                "Commitment verified",
                f"{proposed['name']} meets all customer requirements."
            )
        )

        return {
            "requirements": requirements,
            "proposed_product": proposed,
            "verification": verification,
            "alternative": None,
            "final_status": "VERIFIED",
            "message": (
                f"{proposed['name']} meets all your requirements."
            ),
            "audit_trail": audit,
        }

    # -----------------------------------------------------
    # STEP 5: NO VERIFIED PRODUCT
    # -----------------------------------------------------

    # Select the best matching blocked product
    blocked_products.sort(
        key=lambda item: (
            -calculate_match_score(
                item["product"],
                requirements
            ),
            item["product"].get(
                "price",
                float("inf")
            )
        )
    )

    selected = blocked_products[0]

    proposed = selected["product"]
    verification = selected["verification"]

    audit.append(
        build_audit_entry(
            step,
            "Product selected",
            f"Best matching product: "
            f"{proposed['name']} "
            f"(₹{proposed['price']})."
        )
    )

    step += 1

    # -----------------------------------------------------
    # SHOW FAILED CHECKS
    # -----------------------------------------------------

    for check in verification["checks"]:

        audit.append(
            build_audit_entry(
                step,
                (
                    f"{check['requirement']} "
                    f"{'verified' if check['passed'] else 'FAILED'}"
                ),
                check["detail"]
            )
        )

        step += 1

    failed_reasons = [
        check["detail"]
        for check in verification["checks"]
        if not check["passed"]
    ]

    audit.append(
        build_audit_entry(
            step,
            "Commitment blocked",
            "; ".join(failed_reasons)
        )
    )

    step += 1

    # -----------------------------------------------------
    # STEP 6: ALTERNATIVE SEARCH
    # -----------------------------------------------------

    audit.append(
        build_audit_entry(
            step,
            "Alternative search started",
            "Searching the complete catalog for another "
            "product satisfying all requirements."
        )
    )

    step += 1

    alternative_result = find_alternative(
        catalog,
        proposed,
        requirements
    )

    # -----------------------------------------------------
    # NO ALTERNATIVE
    # -----------------------------------------------------

    if alternative_result is None:

        audit.append(
            build_audit_entry(
                step,
                "No alternative found",
                "No other product in the catalog satisfies "
                "all customer requirements."
            )
        )

        return {
            "requirements": requirements,
            "proposed_product": proposed,
            "verification": verification,
            "alternative": None,
            "final_status": "NO_ALTERNATIVE",
            "message": (
                "The requested product was found, "
                "but no product in the catalog satisfies "
                "all your requirements."
            ),
            "audit_trail": audit,
        }

    # -----------------------------------------------------
    # ALTERNATIVE FOUND
    # -----------------------------------------------------

    alternative = alternative_result["product"]

    alt_verification = alternative_result["verification"]

    audit.append(
        build_audit_entry(
            step,
            "Alternative found",
            f"{alternative['name']} "
            f"(₹{alternative['price']}) "
            f"satisfies all requirements."
        )
    )

    step += 1

    for check in alt_verification["checks"]:

        audit.append(
            build_audit_entry(
                step,
                (
                    f"Alternative: "
                    f"{check['requirement']} "
                    f"{'verified' if check['passed'] else 'FAILED'}"
                ),
                check["detail"]
            )
        )

        step += 1

    # -----------------------------------------------------
    # SELF CORRECTION
    # -----------------------------------------------------

    audit.append(
        build_audit_entry(
            step,
            "Self-correction complete",
            f"{alternative['name']} is VERIFIED "
            f"and offered instead of {proposed['name']}."
        )
    )

    return {
        "requirements": requirements,
        "proposed_product": proposed,
        "verification": verification,
        "alternative": {
            "product": alternative,
            "verification": alt_verification,
        },
        "final_status": "SELF_CORRECTED",
        "message": (
            f"The original product "
            f"({proposed['name']}) could not meet all "
            f"requirements. We found a verified alternative: "
            f"{alternative['name']}."
        ),
        "audit_trail": audit,
    }