def check_email_phone_age_config(region_data) -> list[str]:
    warnings = []
    email_rules = region_data.get('email_rules')

    if not email_rules:
        warnings.append("Warning: 'email_rules' not found in region data. Age-based email/phone logic may not function as expected.")
        return warnings

    age_limits = email_rules.get('age_limits')

    if not age_limits:
        warnings.append("Warning: 'age_limits' not found in 'email_rules'. Age-based email/phone logic may not function as expected.")
        return warnings

    required_keys = [
        'min_email_age',
        'max_email_age',
        'no_email_probability_young',
        'no_email_probability_old',
        'min_phone_age'
    ]

    for key in required_keys:
        if key not in age_limits:
            warnings.append(f"Warning: Missing key '{key}' in 'age_limits' within 'email_rules'. Default values will be used.")

    # Check probability ranges
    for prob_key in ['no_email_probability_young', 'no_email_probability_old']:
        if prob_key in age_limits:
            prob_value = age_limits[prob_key]
            if not (0 <= prob_value <= 1):
                warnings.append(f"Warning: Probability '{prob_key}' ({prob_value}) in 'age_limits' is not between 0 and 1. This may cause unexpected behavior.")

    return warnings
