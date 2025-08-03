import random

def generate_physical_description(region_data, gender, age, hidden_attributes, debug_print_func):
    phys_char_data = region_data['physical_characteristics']
    phys_rules = region_data.get('physical_characteristics_rules', {})
    description = {}
    description['eye_color'] = random.choice(phys_char_data['eye_colors'])
    
    # Hair color based on age using rules
    hair_color_rules = phys_rules.get('hair_color_rules', [])
    selected_hair_color_rule = None
    for rule in hair_color_rules:
        min_age, max_age = rule['age_range']
        if min_age <= age <= max_age:
            selected_hair_color_rule = rule
            break

    if selected_hair_color_rule:
        colors = list(selected_hair_color_rule['colors'].keys())
        weights = list(selected_hair_color_rule['colors'].values())
        if sum(weights) > 0:
            description['hair_color'] = random.choices(colors, weights=weights, k=1)[0]
        else:
            description['hair_color'] = random.choice(phys_char_data['natural_hair_colors'])
    else:
        description['hair_color'] = random.choice(phys_char_data['natural_hair_colors'])

    description['hair_style'] = random.choice(phys_char_data['hair_styles'])
    
    # Height based on age using rules
    height_rules = phys_rules.get('height_rules_cm', [])
    selected_height_rule = None
    for rule in height_rules:
        min_age, max_age = rule['age_range']
        if min_age <= age <= max_age:
            selected_height_rule = rule
            break

    if selected_height_rule:
        height_range = selected_height_rule[gender]
        description['height_cm'] = random.randint(height_range['min'], height_range['max'])
    else:
        # Fallback to general height ranges if no specific rule is found
        height_range = phys_char_data['height_ranges_cm'][gender]
        description['height_cm'] = random.randint(height_range['min'], height_range['max'])
    
    # Build type based on age using rules
    build_type_rules = phys_rules.get('build_type_rules', [])
    selected_build_type_rule = None
    for rule in build_type_rules:
        min_age, max_age = rule['age_range']
        if min_age <= age <= max_age:
            selected_build_type_rule = rule
            break

    if selected_build_type_rule:
        builds = list(selected_build_type_rule['builds'].keys())
        weights = list(selected_build_type_rule['builds'].values())
        if sum(weights) > 0:
            description['build'] = random.choices(builds, weights=weights, k=1)[0]
        else:
            description['build'] = random.choice(phys_char_data['build_types'])
    else:
        description['build'] = random.choice(phys_char_data['build_types'])

    # Distinguishing marks with increased probability for older ages using rules
    marks = []
    mark_probabilities = phys_rules.get('distinguishing_mark_probabilities', {})

    tattoo_rule = mark_probabilities.get('tattoos', {})
    tattoo_prob = 0
    if age >= 18:
        tattoo_prob = tattoo_rule.get('base_probability', 0.2) + (age / 100 * tattoo_rule.get('age_multiplier', 0.3))

    scar_rule = mark_probabilities.get('scars', {})
    scar_prob = scar_rule.get('base_probability', 0.1) + (age / 100 * scar_rule.get('age_multiplier', 0.2))

    birthmark_rule = mark_probabilities.get('birthmarks', {})
    birthmark_prob = birthmark_rule.get('base_probability', 0.05) + (age / 100 * birthmark_rule.get('age_multiplier', 0.1))

    if random.random() < tattoo_prob and phys_char_data['distinguishing_marks']['tattoos']:
        tattoo = random.choice(phys_char_data['distinguishing_marks']['tattoos'])
        marks.append(f"Tattoo: {tattoo['description']} on the {tattoo['location']}")
    if random.random() < scar_prob and phys_char_data['distinguishing_marks']['scars']:
        scar = random.choice(phys_char_data['distinguishing_marks']['scars'])
        marks.append(f"Scar: {scar['description']} on the {scar['location']}")
    if random.random() < birthmark_prob and phys_char_data['distinguishing_marks']['birthmarks']:
        birthmark = random.choice(phys_char_data['distinguishing_marks']['birthmarks'])
        marks.append(f"Birthmark: {birthmark['description']} on the {birthmark['location']}")
    description['distinguishing_marks'] = marks if marks else ['None']

    return description
