import random

def _get_initial_occupations(region_data, age, gender, constraints, debug_print_func, desired_education_level=None):
    # Prioritize 'Student' for young ages
    if age and age < 18: # Assuming 18 is the general age for non-student occupations
        for occ in region_data['occupations']:
            if occ['name'] == 'Student':
                return [occ] # Return only 'Student' if found for young ages

    if constraints.get('occupation'):
        # If a specific occupation is requested, return it directly
        requested_occupation_name = constraints['occupation']
        for occ in region_data['occupations']:
            if occ['name'] == requested_occupation_name:
                return [occ]
        # Fallback if requested occupation is not found
        return []
    if age and age < 6:
        return []

    # Filter occupations by age if age is provided
    if age:
        debug_print_func(f"Content of region_data['occupations']: {region_data['occupations']}")
        valid_occupations = [occ for occ in region_data['occupations'] if occ['min_age'] <= age <= occ['max_age']]
    else:
        valid_occupations = region_data['occupations']['occupations']

    if not valid_occupations:
        return []

    # Prioritize occupations based on desired_education_level if provided
    if desired_education_level:
        education_filtered_occupations = [occ for occ in valid_occupations if occ.get('typical_education_level') == desired_education_level]
        if education_filtered_occupations:
            valid_occupations = education_filtered_occupations # Use education-filtered list if not empty

    # Apply gender bias to weights for initial filtering (before detailed scoring)
    weighted_occupations = []
    weights = []
    for occ in valid_occupations:
        gender_weight = occ['gender_bias'].get(gender, 1.0) # Default to 1.0 if no specific bias
        weighted_occupations.append(occ)
        weights.append(gender_weight)

    # Use random.choices for initial selection based on gender bias
    if sum(weights) == 0:
        return valid_occupations # Fallback to all valid if no weights
    else:
        return random.choices(weighted_occupations, weights=weights, k=len(weighted_occupations)) # Return a list of occupations, potentially with duplicates based on weight

def determine_occupation(profile, region_data, debug_print_func, constraints, hidden_attributes):
    age = profile['age']
    gender = profile['gender']
    hobbies = profile.get('hobbies_interests', [])
    skills = profile.get('skills', [])
    interests = profile.get('interests', [])

    # Get initial list of occupations filtered by age and gender
    potential_occupations = _get_initial_occupations(region_data, age, gender, constraints, debug_print_func, constraints.get('education_level'))

    if not potential_occupations:
        return "Unemployed", {"typical_education_level": "Varies"}

    occupation_scores = []

    for occ in potential_occupations:
        score = 0
        suitability_factors = occ.get('suitability_factors', {})
        debug_print_func(f"  Checking occupation: {occ['name']}")
        debug_print_func(f"    Suitability factors: {suitability_factors}")

        # Score based on hidden attributes
        if 'hidden_attributes' in suitability_factors:
            for attr, bias_rule in suitability_factors['hidden_attributes'].items():
                if attr in hidden_attributes and hidden_attributes[attr] is not None:
                    attr_value = hidden_attributes[attr]
                    if bias_rule[0] <= attr_value <= bias_rule[1]:
                        score += bias_rule[2] if len(bias_rule) > 2 else 1 # Use weight if provided, else 1

        # Score based on hobbies
        if 'hobbies_multipliers' in suitability_factors and hobbies:
            for hobby in hobbies:
                score += suitability_factors['hobbies_multipliers'].get(hobby, 0)

        # Score based on skills
        if 'skills_multipliers' in suitability_factors and skills:
            for skill in skills:
                score += suitability_factors['skills_multipliers'].get(skill, 0)

        # Score based on interests
        if 'interests_multipliers' in suitability_factors and interests:
            for interest in interests:
                score += suitability_factors['interests_multipliers'].get(interest, 0)
        
        occupation_scores.append((occ, score))

    # Sort by score in descending order
    occupation_scores.sort(key=lambda x: x[1], reverse=True)

    # Select the best matching occupation(s)
    if occupation_scores:
        max_score = occupation_scores[0][1]
        best_occupations = [occ for occ, score in occupation_scores if score == max_score]
        
        # If multiple occupations have the same max score, choose one randomly
        selected_occupation = random.choice(best_occupations)
        return selected_occupation['name'], selected_occupation
    else:
        return "Unemployed", {"typical_education_level": "Varies"}

def generate_occupation(region_data, age, occupation_constraint, hidden_attributes):
    """Wrapper function to generate just the occupation string."""
    # We pass a minimal profile and constraints dict for the purpose of this function
    profile = {'age': age, 'gender': 'any'} # Gender is not strictly needed here
    constraints = {'occupation': occupation_constraint}
    occupation_name, _ = determine_occupation(profile, region_data, lambda *a, **kw: None, constraints, hidden_attributes)
    return {"Occupation": occupation_name}