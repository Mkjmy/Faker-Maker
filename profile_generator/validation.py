def validate_profile(profile, region_data, constraints, debug_print_func):
    """Validates a generated profile against consistency rules."""
    age = profile['age']
    allow_unconventional = constraints.get('allow_unconventional', False)
    legal_marriage_age = region_data.get('legal_marriage_age', 18) # Default to 18 if not specified

    # Rule 1: Marital Status vs. Age
    if 'marital_status' in profile:
        marital_status = profile['marital_status']
        if marital_status == 'Married':
            if age < legal_marriage_age:
                if not allow_unconventional:
                    return False, f"Inconsistency: Married at age {age} (below legal marriage age {legal_marriage_age}) in strict mode."

    # Rule 2: Children vs. Age and Marital Status
    if 'children' in profile:
        num_children = profile['children']
        marital_status = profile.get('marital_status')

        if num_children > 0:
            if age < 15: # Arbitrary minimum age to have children
                if not allow_unconventional:
                    return False, f"Inconsistency: Has children at age {age} (too young) in strict mode."
            
            if marital_status == 'Single':
                # In strict mode, a single person having children is an inconsistency unless explicitly allowed
                if not allow_unconventional and num_children > 0:
                    return False, f"Inconsistency: Single with {num_children} children in strict mode."

    # Rule 3: Occupation vs. Age
    if 'occupation' in profile and profile['occupation'] not in ["Not applicable (underage)", "Unemployed"]:
        occ_name = profile['occupation']
        found_occ = next((occ for occ in region_data['occupations']['occupations'] if occ['name'] == occ_name), None)
        if found_occ:
            if not (found_occ['min_age'] <= age <= found_occ['max_age']):
                if not allow_unconventional:
                    return False, f"Inconsistency: Age {age} is outside typical range for {occ_name} in strict mode."

    return True, "Consistent"
