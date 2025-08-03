import re
from datetime import datetime

def check_profile(profile, region_data, constraints, debug_print_func):
    """
    Performs basic validation on a profile.
    Returns a tuple: (is_valid, reasons)
    - is_valid (bool): False if there are any hard errors.
    - reasons (list): A list of strings, each prefixed with [Error], [Warning], or [Logic]
    """
    reasons = []
    has_errors = False

    # Standardize profile keys to lowercase for case-insensitive access
    p = {k.lower(): v for k, v in profile.items()}
    age = p.get('age')

    # 1. Basic Field Presence (Core Fields)
    core_required_fields = ['first_name', 'last_name', 'age', 'gender']
    for field in core_required_fields:
        if p.get(field) is None:
            has_errors = True
            reasons.append(f"[Error] Missing required core field: {field}")

    # 2. Age-DOB Consistency
    if 'age' in p and 'dob' in p and p['dob'] is not None:
        try:
            dob_date = datetime.strptime(p['dob'], '%Y-%m-%d')
            today = datetime.today()
            calculated_age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
            if abs(calculated_age - age) > 1: # Allow for a 1-year discrepancy
                has_errors = True
                reasons.append(f"[Error] Age ({age}) and DOB ({p['dob']}) are inconsistent. Calculated age: {calculated_age}")
        except (ValueError, TypeError):
            has_errors = True
            reasons.append(f"[Error] Invalid DOB format: {p['dob']}")

    # 3. Age-conditional fields (Email/Phone)
    email = p.get('email')
    phone_number = p.get('phone_number')
    email_rules = region_data.get('email_rules', {})
    age_limits = email_rules.get('age_limits', {})

    min_email_age = age_limits.get('min_email_age', 13)
    max_email_age = age_limits.get('max_email_age', 85)
    min_phone_age = age_limits.get('min_phone_age', 16)

    if isinstance(age, int):
        # Email check
        if email is None:
            if min_email_age <= age <= max_email_age:
                has_errors = True
                reasons.append(f"[Error] Missing required field: email for age {age}.")
            else:
                reasons.append(f"[Logic] Profile has no email, which is reasonable for age {age}.")
        else: # Email is present
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                has_errors = True
                reasons.append(f"[Error] Invalid email format: {email}")
            if age > max_email_age or age < min_email_age:
                 reasons.append(f"[Warning] Profile has an email at age {age}, which is uncommon.")

        # Phone number check
        if phone_number is None:
            if age >= min_phone_age:
                has_errors = True
                reasons.append(f"[Error] Missing required field: phone_number for age {age}.")
            else:
                reasons.append(f"[Logic] Profile has no phone number, which is reasonable for age {age}.")
        else: # Phone is present
            if not re.match(r"^[0-9\-\(\)\s\+]+$", phone_number):
                has_errors = True
                reasons.append(f"[Error] Invalid phone number format: {phone_number}")
    else: # Age is not an int, so we can't do age-based checks. Assume required.
        if email is None:
            has_errors = True
            reasons.append("[Error] Missing required field: email")
        if phone_number is None:
            has_errors = True
            reasons.append("[Error] Missing required field: phone_number")

    return not has_errors, reasons
