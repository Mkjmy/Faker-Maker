import random

def _get_weighted_choice(options, hidden_attributes_dict):
    weighted_options = []
    weights = []
    for option in options:
        base_weight = 1
        
        if isinstance(option, dict) and 'hidden_attribute_biases' in option:
            for attr, bias_rule in option['hidden_attribute_biases'].items():
                if attr in hidden_attributes_dict:
                    attr_value = hidden_attributes_dict[attr]
                    if bias_rule['min'] <= attr_value <= bias_rule['max']:
                        base_weight *= bias_rule['weight']
        weighted_options.append(option)
        weights.append(base_weight)
    
    if not weighted_options:
        return None

    # Normalize weights to avoid issues with random.choices if all weights are 0
    total_weight = sum(weights)
    if total_weight == 0:
        # If all weights are zero, give equal probability to all options
        return random.choice([opt['name'] if isinstance(opt, dict) else opt for opt in options])
    else:
        normalized_weights = [w / total_weight for w in weights]
        selected_option = random.choices(weighted_options, weights=normalized_weights, k=1)[0]
        return selected_option['name'] if isinstance(selected_option, dict) else selected_option

def _apply_numerical_bias(initial_score, biases, min_val=0, max_val=1000):
    """Applies a list of numerical biases to an initial score."""
    if not biases:
        return initial_score

    # Simple approach: average the midpoints of the bias ranges, weighted by their weights.
    # Then, adjust the initial score towards this weighted average.
    
    weighted_sum_midpoints = 0
    total_weight = 0
    
    for bias in biases:
        midpoint = (bias['min'] + bias['max']) / 2
        weight = bias['weight']
        weighted_sum_midpoints += midpoint * weight
        total_weight += weight
    
    if total_weight == 0:
        return initial_score # No effective biases

    weighted_average_midpoint = weighted_sum_midpoints / total_weight
    
    # Adjust the initial score towards the weighted average midpoint.
    # The strength of adjustment can be proportional to total_weight or a fixed factor.
    # For simplicity, let's move the score a fraction of the way towards the midpoint.
    adjustment_factor = 0.3 # How strongly the bias influences the score (0.0 to 1.0)
    adjusted_score = initial_score + (weighted_average_midpoint - initial_score) * adjustment_factor
    
    # Ensure the score stays within the valid range
    return max(min_val, min(max_val, int(adjusted_score)))


def generate_hidden_attributes(unconventional_data_rules, profile: dict, constraints: dict, debug_print_func, skills_interests_rules, region_data):
    debug_print_func("Generating hidden attributes with all relevant biases...")
    hidden_attributes = {}

    # Define default ranges for numerical hidden attributes (0-1000)
    numerical_attributes_defaults = {
        'cognitive_style_score': {'min': 0, 'max': 1000},
        'performative_tendency': {'min': 0, 'max': 1000},
        'social_web_density': {'min': 0, 'max': 1000},
        'routine_predictability': {'min': 0, 'max': 1000},
        'stability_index': {'min': 0, 'max': 1000},
        'impulse_control': {'min': 0, 'max': 1000},
        'communication_formality': {'min': 0, 'max': 1000},
        'curiosity_drive': {'min': 0, 'max': 1000},
        'autonomy_level': {'min': 0, 'max': 1000},
        'context_switching_agility': {'min': 0, 'max': 1000},
        'ambiguity_tolerance': {'min': 0, 'max': 1000},
        'metacognition_awareness': {'min': 0, 'max': 1000},
        'trust_propensity': {'min': 0, 'max': 1000},
        'delayed_gratification_score': {'min': 0, 'max': 1000},
        'moral_flexibility': {'min': 0, 'max': 1000},
        'cognitive_load_tolerance': {'min': 0, 'max': 1000},
        'inner_narrative_intensity': {'min': 0, 'max': 1000}
    }

    # Initialize bias collectors
    all_numerical_biases = {attr: [] for attr in numerical_attributes_defaults}
    personality_trait_biases = []

    # 1. Collect biases from Hobbies
    selected_hobbies = constraints.get('hobbies', [])
    if skills_interests_rules:
        for category in ['age_based_hobbies', 'occupation_based_hobbies', 'education_based_hobbies']:
            if category in skills_interests_rules:
                for group in skills_interests_rules[category]:
                    for hobby_data in group['hobbies']:
                        if hobby_data['name'] in selected_hobbies:
                            if 'hidden_attribute_biases' in hobby_data:
                                for attr, bias_rule in hobby_data['hidden_attribute_biases'].items():
                                    if attr in all_numerical_biases:
                                        all_numerical_biases[attr].append(bias_rule)
                            if 'personality_trait_bias' in hobby_data:
                                personality_trait_biases.append(hobby_data['personality_trait_bias'])

    # 2. Collect biases from Occupation
    selected_occupation = constraints.get('occupation')
    occupation_rules = region_data.get('occupation_rules', {})
    if selected_occupation and 'occupation_biases' in occupation_rules:
        for occ_bias_data in occupation_rules['occupation_biases']:
            if occ_bias_data['occupation'].lower() == selected_occupation.lower():
                if 'hidden_attribute_biases' in occ_bias_data:
                    for attr, bias_rule in occ_bias_data['hidden_attribute_biases'].items():
                        if attr in all_numerical_biases:
                            all_numerical_biases[attr].append(bias_rule)
                if 'personality_trait_bias' in occ_bias_data:
                    personality_trait_biases.append(occ_bias_data['personality_trait_bias'])

    # 3. Collect biases from Marital Status
    selected_marital_status = constraints.get('marital_status')
    family_details_rules = region_data.get('family_details_rules', {})
    if selected_marital_status and 'marital_status_biases' in family_details_rules:
        for ms_bias_data in family_details_rules['marital_status_biases']:
            if ms_bias_data['status'].lower() == selected_marital_status.lower():
                if 'hidden_attribute_biases' in ms_bias_data:
                    for attr, bias_rule in ms_bias_data['hidden_attribute_biases'].items():
                        if attr in all_numerical_biases:
                            all_numerical_biases[attr].append(bias_rule)
                if 'personality_trait_bias' in ms_bias_data:
                    personality_trait_biases.append(ms_bias_data['personality_trait_bias'])

    # 4. Collect biases from Education Level
    selected_education_level = constraints.get('desired_education_level')
    if skills_interests_rules and 'education_based_hobbies' in skills_interests_rules:
        for edu_group in skills_interests_rules['education_based_hobbies']:
            if selected_education_level and selected_education_level.lower() in [level.lower() for level in edu_group.get('education_levels', [])]:
                for hobby_data in edu_group['hobbies']:
                    # Assuming education-based hobbies also have biases directly or indirectly
                    if 'hidden_attribute_biases' in hobby_data:
                        for attr, bias_rule in hobby_data['hidden_attribute_biases'].items():
                            if attr in all_numerical_biases:
                                all_numerical_biases[attr].append(bias_rule)
                    if 'personality_trait_bias' in hobby_data:
                        personality_trait_biases.append(hobby_data['personality_trait_bias'])

    # 5. Collect biases from Location
    selected_location_name = constraints.get('location', {}).get('province') or \
                             constraints.get('location', {}).get('city') # Assuming 'city' might also be a top-level selection

    if selected_location_name:
        location_data = region_data.get('address_data', {})
        found_province = None
        for region_entry in location_data.get('regions', []):
            for province_entry in region_entry.get('provinces', []):
                if province_entry['name'] == selected_location_name:
                    found_province = province_entry
                    break
            if found_province:
                break
        
        if found_province:
            debug_print_func(f"Found province data for {selected_location_name}: {found_province}")
            location_biases_rules = region_data.get('location_biases', {}).get('location_biases', [])
            
            for bias_rule in location_biases_rules:
                condition_met = True
                for condition_key, condition_value in bias_rule.get('condition', {}).items():
                    if condition_key == 'terrain_type' and found_province.get('geography', {}).get('terrain_type') != condition_value:
                        condition_met = False
                        break
                    elif condition_key == 'economic_classification' and found_province.get('economy', {}).get('economic_classification') != condition_value:
                        condition_met = False
                        break
                    elif condition_key == 'tourism_status' and found_province.get('tourism_status') != condition_value:
                        condition_met = False
                        break
                
                if condition_met:
                    debug_print_func(f"Applying location bias rule: {bias_rule}")
                    for attr, change_rule in bias_rule.get('attribute_biases', {}).items():
                        if attr in numerical_attributes_defaults:
                            # Apply the change directly to the initial score generation
                            # This will be handled in the loop below where initial_score is generated
                            # For now, we just collect these biases
                            all_numerical_biases[attr].append({
                                'min': change_rule['min_change'],
                                'max': change_rule['max_change'],
                                'weight': 1 # Default weight for location biases
                            })
                            
    # Initialize bias collectors
    all_numerical_biases = {attr: [] for attr in numerical_attributes_defaults}
    personality_trait_biases = []
    location_numerical_biases = {attr: [] for attr in numerical_attributes_defaults}

    # 1. Collect biases from Hobbies
    selected_hobbies = constraints.get('hobbies', [])
    if skills_interests_rules:
        for category in ['age_based_hobbies', 'occupation_based_hobbies', 'education_based_hobbies']:
            if category in skills_interests_rules:
                for group in skills_interests_rules[category]:
                    for hobby_data in group['hobbies']:
                        if hobby_data['name'] in selected_hobbies:
                            if 'hidden_attribute_biases' in hobby_data:
                                for attr, bias_rule in hobby_data['hidden_attribute_biases'].items():
                                    if attr in all_numerical_biases:
                                        all_numerical_biases[attr].append(bias_rule)
                            if 'personality_trait_bias' in hobby_data:
                                personality_trait_biases.append(hobby_data['personality_trait_bias'])

    # 2. Collect biases from Occupation
    selected_occupation = constraints.get('occupation')
    occupation_rules = region_data.get('occupation_rules', {})
    if selected_occupation and 'occupation_biases' in occupation_rules:
        for occ_bias_data in occupation_rules['occupation_biases']:
            if occ_bias_data['occupation'].lower() == selected_occupation.lower():
                if 'hidden_attribute_biases' in occ_bias_data:
                    for attr, bias_rule in occ_bias_data['hidden_attribute_biases'].items():
                        if attr in all_numerical_biases:
                            all_numerical_biases[attr].append(bias_rule)
                if 'personality_trait_bias' in occ_bias_data:
                    personality_trait_biases.append(occ_bias_data['personality_trait_bias'])

    # 3. Collect biases from Marital Status
    selected_marital_status = constraints.get('marital_status')
    family_details_rules = region_data.get('family_details_rules', {})
    if selected_marital_status and 'marital_status_biases' in family_details_rules:
        for ms_bias_data in family_details_rules['marital_status_biases']:
            if ms_bias_data['status'].lower() == selected_marital_status.lower():
                if 'hidden_attribute_biases' in ms_bias_data:
                    for attr, bias_rule in ms_bias_data['hidden_attribute_biases'].items():
                        if attr in all_numerical_biases:
                            all_numerical_biases[attr].append(bias_rule)
                if 'personality_trait_bias' in ms_bias_data:
                    personality_trait_biases.append(ms_bias_data['personality_trait_bias'])

    # 4. Collect biases from Education Level
    selected_education_level = constraints.get('desired_education_level')
    if skills_interests_rules and 'education_based_hobbies' in skills_interests_rules:
        for edu_group in skills_interests_rules['education_based_hobbies']:
            if selected_education_level and selected_education_level.lower() in [level.lower() for level in edu_group.get('education_levels', [])]:
                for hobby_data in edu_group['hobbies']:
                    # Assuming education-based hobbies also have biases directly or indirectly
                    if 'hidden_attribute_biases' in hobby_data:
                        for attr, bias_rule in hobby_data['hidden_attribute_biases'].items():
                            if attr in all_numerical_biases:
                                all_numerical_biases[attr].append(bias_rule)
                    if 'personality_trait_bias' in hobby_data:
                        personality_trait_biases.append(hobby_data['personality_trait_bias'])

    # 5. Collect biases from Location
    selected_location_name = constraints.get('location', {}).get('province') or \
                             constraints.get('location', {}).get('city') # Assuming 'city' might also be a top-level selection

    if selected_location_name:
        location_data = region_data.get('address_data', {})
        found_province = None
        for region_entry in location_data.get('regions', []):
            for province_entry in region_entry.get('provinces', []):
                if province_entry['name'] == selected_location_name:
                    found_province = province_entry
                    break
            if found_province:
                break
        
        if found_province:
            debug_print_func(f"Found province data for {selected_location_name}: {found_province}")
            location_biases_rules = region_data.get('location_biases', {}).get('location_biases', [])
            
            for bias_rule in location_biases_rules:
                condition_met = True
                for condition_key, condition_value in bias_rule.get('condition', {}).items():
                    if condition_key == 'terrain_type' and found_province.get('geography', {}).get('terrain_type') != condition_value:
                        condition_met = False
                        break
                    elif condition_key == 'economic_classification' and found_province.get('economy', {}).get('economic_classification') != condition_value:
                        condition_met = False
                        break
                    elif condition_key == 'tourism_status' and found_province.get('tourism_status') != condition_value:
                        condition_met = False
                        break
                
                if condition_met:
                    debug_print_func(f"Applying location bias rule: {bias_rule}")
                    for attr, change_rule in bias_rule.get('attribute_biases', {}).items():
                        if attr in numerical_attributes_defaults:
                            location_numerical_biases[attr].append({
                                'min_change': change_rule['min_change'],
                                'max_change': change_rule['max_change']
                            })

    # Generate/infer numerical hidden attributes
    for attr, default_range in numerical_attributes_defaults.items():
        if constraints.get(attr) is not None: # Check if explicitly set by CLI flag
            hidden_attributes[attr] = constraints[attr]
        else:
            initial_score = random.randint(default_range['min'], default_range['max'])
            
            # Apply location biases directly to initial_score
            for loc_bias in location_numerical_biases.get(attr, []):
                initial_score += random.randint(loc_bias['min_change'], loc_bias['max_change'])
            initial_score = max(default_range['min'], min(default_range['max'], int(initial_score))) # Clamp after location bias

            # Apply other collected biases (hobbies, occupation, marital status, education) using _apply_numerical_bias
            adjusted_score = _apply_numerical_bias(initial_score, all_numerical_biases[attr], default_range['min'], default_range['max'])
            hidden_attributes[attr] = adjusted_score

    # Personality Trait
    if constraints.get('personality_trait') is not None:
        hidden_attributes['personality_trait'] = constraints['personality_trait']
    else:
        # If personality_trait_biases exist, we could try to bias the selection.
        # For now, without a score-to-trait mapping, it remains random if not explicitly set.
        # A more advanced implementation would map traits to scores and apply biases.
        hidden_attributes['personality_trait'] = _get_weighted_choice(unconventional_data_rules['personality_traits'], hidden_attributes)

    # Exceptionality Score (1-100)
    if constraints.get('exceptionality_score') is not None:
        hidden_attributes['exceptionality_score'] = constraints['exceptionality_score']
    else:
        # Could potentially bias this based on personality_trait_biases weight, but keeping it simple for now.
        hidden_attributes['exceptionality_score'] = random.randint(1, 100)

    return hidden_attributes

def generate_unconventional_data(unconventional_data_rules, age, unconventional_data_selection: dict, hidden_attributes: dict, debug_print_func):
    data = {}

    if unconventional_data_selection.get('life_events'):
        possible_life_events = []
        for event_rule in unconventional_data_rules['life_events']:
            min_age, max_age = event_rule['age_range']
            if min_age <= age <= max_age:
                possible_life_events.append(event_rule['event'])
        
        num_events = random.randint(0, min(len(possible_life_events), 3)) # Generate between 0 and 3 events
        data['life_events'] = random.sample(possible_life_events, num_events) if possible_life_events else []

    if unconventional_data_selection.get('online_behaviors'):
        data['online_behavior'] = _get_weighted_choice(unconventional_data_rules['online_behaviors'], hidden_attributes)

    if unconventional_data_selection.get('texting_typing_style'):
        data['texting_typing_style'] = _get_weighted_choice(unconventional_data_rules['texting_typing_styles'], hidden_attributes)

    if unconventional_data_selection.get('digital_footprint'):
        data['digital_footprint'] = _get_weighted_choice(unconventional_data_rules['digital_footprints'], hidden_attributes)

    if unconventional_data_selection.get('device_habits'):
        data['device_habits'] = _get_weighted_choice(unconventional_data_rules['device_habits'], hidden_attributes)

    return data