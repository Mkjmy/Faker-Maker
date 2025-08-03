import random
import unicodedata
from datetime import datetime

def strip_accents(s):
    s = s.replace('đ', 'd').replace('Đ', 'D') # Handle Vietnamese 'đ' character
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')

def generate_email_address(first_name, last_name, middle_name, region_data, age, occupation, education_level, debug_print_func):
    # Ensure age is an integer, default to 0 if None or not an integer
    if age is None or not isinstance(age, int):
        age = 0

    email_rules = region_data.get('email_rules', {})
    
    # Check age limits for email generation
    age_limits = email_rules.get('age_limits', {})
    min_email_age = age_limits.get('min_email_age', 0)
    max_email_age = age_limits.get('max_email_age', 120)
    no_email_prob_young = age_limits.get('no_email_probability_young', 0)
    no_email_prob_old = age_limits.get('no_email_probability_old', 0)

    if age < min_email_age and random.random() < no_email_prob_young:
        return None
    if age > max_email_age and random.random() < no_email_prob_old:
        return None

    # Domains from the specific region's email file
    region_domains = region_data.get('email_domains', [])

    selected_domain = None
    local_part = ""
    current_year = datetime.now().year
    birth_year = current_year - age

    unaccented_first_name = strip_accents(first_name.lower() if first_name else '')
    unaccented_last_name = strip_accents(last_name.lower() if last_name else '')
    unaccented_middle_name = strip_accents(middle_name.lower() if middle_name else '')

    # Find the most appropriate email generation rule based on age
    selected_rule = None
    for rule in email_rules.get('email_generation_rules', []):
        min_age, max_age = rule['age_range']
        if min_age <= age <= max_age:
            selected_rule = rule
            break

    if selected_rule:
        # Determine local part style
        local_part_styles = selected_rule.get('local_part_styles', {})
        if region_data.get('region_id') == 'VN_GENERAL':
            # Prioritize Vietnamese-specific styles that include middle name
            vietnamese_styles = {
                "first_middle_last_year": 0.2,
                "first_middle_last_random_number": 0.2,
                "first_middle_last_dot_year": 0.2,
                "first_middle_last_dot_random_number": 0.2,
                "first_middle_last_initial_year": 0.1,
                "first_middle_last_initial_random_number": 0.1
            }
            # Merge with general styles, giving Vietnamese styles priority
            combined_styles = {**local_part_styles, **vietnamese_styles}
            if combined_styles and sum(combined_styles.values()) > 0:
                chosen_style = random.choices(list(combined_styles.keys()), weights=list(combined_styles.values()), k=1)[0]
            else:
                chosen_style = "first_last_random_number" # Fallback
        else:
            if local_part_styles and sum(local_part_styles.values()) > 0:
                chosen_style = random.choices(list(local_part_styles.keys()), weights=list(local_part_styles.values()), k=1)[0]
            else:
                chosen_style = "first_last_random_number" # Fallback

        if region_data.get('region_id') == 'VN_GENERAL':
            if chosen_style == "first_middle_last_year":
                local_part = f"{unaccented_first_name}{unaccented_middle_name}{unaccented_last_name}{birth_year}"
            elif chosen_style == "first_middle_last_random_number":
                local_part = f"{unaccented_first_name}{unaccented_middle_name}{unaccented_last_name}{random.randint(1,99)}"
            elif chosen_style == "first_middle_last_dot_year":
                local_part = f"{unaccented_first_name}.{unaccented_middle_name}.{unaccented_last_name}{birth_year}"
            elif chosen_style == "first_middle_last_dot_random_number":
                local_part = f"{unaccented_first_name}.{unaccented_middle_name}.{unaccented_last_name}{random.randint(1,99)}"
            elif chosen_style == "first_middle_last_initial_year":
                local_part = f"{unaccented_first_name}{unaccented_middle_name[0] if unaccented_middle_name else ''}{unaccented_last_name}{birth_year}"
            elif chosen_style == "first_middle_last_initial_random_number":
                local_part = f"{unaccented_first_name}{unaccented_middle_name[0] if unaccented_middle_name else ''}{unaccented_last_name}{random.randint(1,99)}"
            else:
                # Fallback to existing styles if no specific middle name style is chosen
                if chosen_style == "nickname_random_number":
                    nicknames = region_data.get('nicknames', {}).get('nicknames', [])
                    if nicknames:
                        local_part = strip_accents(random.choice(nicknames).lower())
                        local_part += str(random.randint(1,99))
                    else:
                        local_part = f"{unaccented_first_name}{random.randint(1,99)}"
                elif chosen_style == "nickname_idol":
                    idol_nicknames = email_rules.get('idol_nicknames', [])
                    if idol_nicknames:
                        local_part = random.choice(idol_nicknames).lower()
                        local_part += str(random.randint(1,999))
                    else:
                        local_part = f"{unaccented_first_name}{random.randint(1,99)}"
                elif chosen_style == "first_name_random_number":
                    local_part = f"{unaccented_first_name}{random.randint(1,99)}"
                elif chosen_style == "first_last_initial_year":
                    local_part = f"{unaccented_first_name}{unaccented_last_name[0]}{str(birth_year)[-2:]}"
                elif chosen_style == "first_last_random_number":
                    local_part = f"{unaccented_first_name}{unaccented_last_name}{random.randint(1,99)}"
                elif chosen_style == "first_last_year":
                    local_part = f"{unaccented_first_name}{unaccented_last_name}{birth_year}"
                elif chosen_style == "first_last_dot_year":
                    local_part = f"{unaccented_first_name}.{unaccented_last_name}{birth_year}"
                elif chosen_style == "first_last_work":
                    local_part = f"{unaccented_first_name}{unaccented_last_name}.work"
                elif chosen_style == "first_last_location":
                    # This is a placeholder, actual location abbreviation logic would be more complex
                    location_abbr = "hcm" # Example for Ho Chi Minh City
                    local_part = f"{unaccented_first_name}{unaccented_last_name}.{location_abbr}"
                elif chosen_style == "simple_name":
                    local_part = f"{unaccented_first_name}{unaccented_last_name}"
                else:
                    local_part = f"{unaccented_first_name}{unaccented_last_name}{random.randint(1,99)}" # Default fallback
        else:
            # Existing logic for non-Vietnamese profiles
            if chosen_style == "nickname_random_number":
                nicknames = region_data.get('nicknames', {}).get('nicknames', [])
                debug_print_func(f"email_generator.py - Nicknames: {nicknames}")
                if nicknames:
                    local_part = strip_accents(random.choice(nicknames).lower())
                    local_part += str(random.randint(1,99))
                else:
                    local_part = f"{unaccented_first_name}{random.randint(1,99)}"
            elif chosen_style == "nickname_idol":
                idol_nicknames = email_rules.get('idol_nicknames', [])
                if idol_nicknames:
                    local_part = random.choice(idol_nicknames).lower()
                    local_part += str(random.randint(1,999))
                else:
                    local_part = f"{unaccented_first_name}{random.randint(1,99)}"
            elif chosen_style == "first_name_random_number":
                local_part = f"{unaccented_first_name}{random.randint(1,99)}"
            elif chosen_style == "first_last_initial_year":
                local_part = f"{unaccented_first_name}{unaccented_last_name[0]}{str(birth_year)[-2:]}"
            elif chosen_style == "first_last_random_number":
                local_part = f"{unaccented_first_name}{unaccented_last_name}{random.randint(1,99)}"
            elif chosen_style == "first_last_year":
                local_part = f"{unaccented_first_name}{unaccented_last_name}{birth_year}"
            elif chosen_style == "first_last_dot_year":
                local_part = f"{unaccented_first_name}.{unaccented_last_name}{birth_year}"
            elif chosen_style == "first_last_work":
                local_part = f"{unaccented_first_name}{unaccented_last_name}.work"
            elif chosen_style == "first_last_location":
                # This is a placeholder, actual location abbreviation logic would be more complex
                location_abbr = "hcm" # Example for Ho Chi Minh City
                local_part = f"{unaccented_first_name}{unaccented_last_name}.{location_abbr}"
            elif chosen_style == "simple_name":
                local_part = f"{unaccented_first_name}{unaccented_last_name}"
            else:
                local_part = f"{unaccented_first_name}{unaccented_last_name}{random.randint(1,99)}" # Default fallback
        # Determine domain
        # Prioritize occupation-based domains
        occupation_based_domains = selected_rule.get('occupation_based_domains', {})
        if occupation_based_domains and occupation in occupation_based_domains:
            domain_weights = occupation_based_domains[occupation]
            if sum(domain_weights.values()) > 0:
                selected_domain = random.choices(list(domain_weights.keys()), weights=list(domain_weights.values()), k=1)[0]

        # Prioritize education-based domains if no occupation-based domain was selected
        if selected_domain is None:
            education_based_domains = selected_rule.get('education_based_domains', {})
            if education_based_domains and education_level in education_based_domains:
                domain_weights = education_based_domains[education_level]
                if sum(domain_weights.values()) > 0:
                    selected_domain = random.choices(list(domain_weights.keys()), weights=list(domain_weights.values()), k=1)[0]
        
        # If no education-based or occupation-based domain, use rule's domains
        if selected_domain is None:
            rule_domains = selected_rule.get('domains', {})
            if rule_domains and sum(rule_domains.values()) > 0:
                selected_domain = random.choices(list(rule_domains.keys()), weights=list(rule_domains.values()), k=1)[0]

        # Legacy domain retention
        if selected_domain and random.random() < selected_rule.get('legacy_domain_retention_probability', 0):
            legacy_domains = [d for d in region_domains if d in ["yahoo.com", "hotmail.com", "live.com"]]
            if legacy_domains:
                selected_domain = random.choice(legacy_domains)

    # Fallback if no specific rule matched or domain not selected
    if selected_domain is None:
        default_domain_weights = email_rules.get('default_domain_weights', {})
        if default_domain_weights and sum(default_domain_weights.values()) > 0:
            filtered_default_domains = {d: w for d, w in default_domain_weights.items() if d in region_domains}
            if filtered_default_domains and sum(filtered_default_domains.values()) > 0:
                selected_domain = random.choices(list(filtered_default_domains.keys()), weights=list(filtered_default_domains.values()), k=1)[0]
            else:
                selected_domain = random.choice(region_domains) if region_domains else None # Fallback to any region domain
        else:
            selected_domain = random.choice(region_domains) # Fallback to any region domain

    if not selected_domain:
        return None # Should not happen if region_domains is not empty

    # Ensure local_part is generated even if no specific style was chosen or if names are missing
    if not local_part:
        if unaccented_first_name and unaccented_last_name:
            local_part = f"{unaccented_first_name}{unaccented_last_name}{random.randint(1,99)}"
        elif unaccented_first_name:
            local_part = f"{unaccented_first_name}{random.randint(1,999)}"
        elif unaccented_last_name:
            local_part = f"{unaccented_last_name}{random.randint(1,999)}"
        else:
            local_part = f"user{random.randint(1000,9999)}" # Generic fallback

    return f"{local_part}@{selected_domain}"

def generate_email(profile, region_data, constraints, hidden_attributes):
    """Wrapper function to generate just the email string."""
    email = generate_email_address(
        profile.get('first_name'),
        profile.get('last_name'),
        profile.get('middle_name'),
        region_data,
        profile.get('age'),
        profile.get('Occupation'), # This key is correct as generated by generate_occupation
        constraints.get('education_level'), # Get education_level from constraints
        lambda *a, **kw: None
    )
    return {"Email": email}

