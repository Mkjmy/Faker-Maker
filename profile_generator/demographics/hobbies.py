def generate_hobbies_interests(age, region_data, hidden_attributes, personality_trait=None, debug_print_func=None):
    hobbies = set() # Use a set to automatically handle duplicates
    hobbies_rules = region_data.get('hobbies_rules', {})

    # hobbies_multipliers are now part of the occupation suitability factors, which are determined later.
    # So, we remove this logic from here.
    hobbies_multipliers = {}

    def _get_weighted_hobby_choice(options, hidden_attributes_dict, multipliers):
        weighted_options = []
        weights = []
        for option in options:
            hobby_name = option['name']
            base_weight = 1

            # Apply hidden attribute biases
            if 'hidden_attribute_biases' in option and hidden_attributes_dict:
                for attr, bias_rule in option['hidden_attribute_biases'].items():
                    if attr in hidden_attributes_dict:
                        attr_value = hidden_attributes_dict[attr]
                        if bias_rule['min'] <= attr_value <= bias_rule['max']:
                            base_weight *= bias_rule['weight']
            
            # Apply personality trait bias
            if 'personality_trait_bias' in option and personality_trait is not None:
                bias_rule = option['personality_trait_bias']
                if bias_rule['min'] <= personality_trait <= bias_rule['max']:
                    base_weight *= bias_rule['weight']
            
            weighted_options.append(hobby_name)
            weights.append(base_weight)
        
        if not weighted_options:
            return None

        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(weighted_options)
        else:
            normalized_weights = [w / total_weight for w in weights]
            return random.choices(weighted_options, weights=normalized_weights, k=1)[0]

    # Age-based hobbies (always select a few)
    for rule in hobbies_rules.get('age_based_hobbies', []):
        min_age, max_age = rule['age_range']
        if min_age <= age <= max_age:
            if rule['hobbies']:
                filtered_hobbies_options = rule['hobbies']
                # Apply 90% rule for elderly people not using internet
                if age >= 60 and random.random() < 0.9: # 90% chance for elderly not to have internet hobbies
                    internet_hobbies = ["social media", "gaming", "coding", "coding side projects"]
                    filtered_hobbies_options = [
                        hobby for hobby in rule['hobbies']
                        if hobby['name'] not in internet_hobbies
                    ]
                
                # Use the new weighted choice function
                selected_hobbies = []
                num_hobbies_to_add = random.randint(1, min(len(filtered_hobbies_options), 3))
                for _ in range(num_hobbies_to_add):
                    selected_hobbies.append(_get_weighted_hobby_choice(filtered_hobbies_options, hidden_attributes, hobbies_multipliers))
                hobbies.update(selected_hobbies)
            break

    # Occupation-based hobbies (will be handled by the occupation determination logic)
    # Education level based hobbies (will be handled by the occupation determination logic)

    return list(hobbies)