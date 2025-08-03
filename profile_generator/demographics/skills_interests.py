def generate_skills_interests(age, skills_interests_rules, hidden_attributes, personality_trait=None, debug_print_func=None):
    skills = []
    interests = []

    def _get_weighted_skill_choice(options, hidden_attributes_dict):
        weighted_options = []
        weights = []
        for option in options:
            skill_name = option['name'] if isinstance(option, dict) else option
            base_weight = 1
            
            if isinstance(option, dict) and 'hidden_attribute_biases' in option:
                for attr, bias_rule in option['hidden_attribute_biases'].items():
                    if attr in hidden_attributes_dict:
                        attr_value = hidden_attributes_dict[attr]
                        if bias_rule['min'] <= attr_value <= bias_rule['max']:
                            base_weight *= bias_rule['weight']
            
            # Apply personality trait bias
            if isinstance(option, dict) and 'personality_trait_bias' in option and personality_trait is not None:
                bias_rule = option['personality_trait_bias']
                if bias_rule['min'] <= personality_trait <= bias_rule['max']:
                    base_weight *= bias_rule['weight']
            
            weighted_options.append(skill_name)
            weights.append(base_weight)
        
        if not weighted_options:
            return None

        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(weighted_options)
        else:
            normalized_weights = [w / total_weight for w in weights]
            return random.choices(weighted_options, weights=normalized_weights, k=1)[0]

    # Age-based skills
    for rule in skills_interests_rules['age_based_skills']:
        min_age, max_age = rule['age_range']
        if min_age <= age <= max_age:
            if rule['skills']:
                # Ensure skills are in object format for weighted choice
                formatted_skills = [s if isinstance(s, dict) else {"name": s} for s in rule['skills']]
                
                # Apply 90% rule for elderly people not using internet
                if age >= 60 and random.random() < 0.9: # 90% chance for elderly not to have internet skills
                    internet_skills = ["digital literacy", "programming", "debugging", "system design", "data analysis", "cloud computing"]
                    formatted_skills = [
                        skill for skill in formatted_skills
                        if skill['name'] not in internet_skills
                    ]

                selected_skill = _get_weighted_skill_choice(formatted_skills, hidden_attributes)
                if selected_skill: # Ensure a skill was actually selected
                    skills.append(selected_skill)
            break

    # General interests
    filtered_interests_options = skills_interests_rules['interests']
    if age >= 60 and random.random() < 0.9: # 90% chance for elderly not to have internet interests
        internet_interests = ["gaming", "coding", "technology", "robotics", "artificial intelligence", "space exploration", "futurism"]
        filtered_interests_options = [
            interest for interest in skills_interests_rules['interests']
            if interest not in internet_interests
        ]

    interests.extend(random.sample(filtered_interests_options, k=random.randint(2, min(5, len(filtered_interests_options)))))

    # Remove duplicates and limit to a reasonable number
    skills = list(set(skills))
    interests = list(set(interests))

    return skills, interests
