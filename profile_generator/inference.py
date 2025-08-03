

def infer_age_from_occupation(constraints, region_data, debug_print_func):
    """If occupation is set and age is not, infer a suitable age range."""
    if 'occupation' in constraints and 'age_range' not in constraints:
        occupation_name = constraints['occupation']
        for occ in region_data.get('occupations', {}).get('occupations', []):
            if occ['name'] == occupation_name:
                min_age = occ.get('min_age', 18)
                max_age = occ.get('max_age', 65)
                constraints['age_range'] = (min_age, max_age)
                debug_print_func(f"Inferred age range {constraints['age_range']} from occupation {occupation_name}")
                return constraints
    return constraints

def infer_marital_status_from_age(constraints, region_data, debug_print_func):
    """If age is set and marital status is not, infer a suitable marital status."""
    if 'age_range' in constraints and 'marital_status' not in constraints:
        age = constraints['age_range'][1]  # Use the max age for simplicity
        legal_marriage_age = region_data.get('legal_marriage_age', 18)
        if age < legal_marriage_age:
            constraints['marital_status'] = 'Single'
            debug_print_func(f"Inferred marital status 'Single' from age {age}")
    return constraints

# This is a placeholder for a more complex rule. The current occupation determination
# already handles this logic, so we will integrate it there.
def infer_occupation_from_skills(constraints, region_data, debug_print_func):
    """If skills are provided, infer a suitable occupation."""
    # The main `determine_occupation` function already implements this logic.
    # We will ensure it's called correctly in the main generation flow.
    pass
    return constraints

INFERENCE_RULES = [
    infer_age_from_occupation,
    infer_marital_status_from_age,
    infer_occupation_from_skills,
]

def run_inference_engine(constraints, region_data, debug_print_func):
    """
    Runs a set of inference rules to derive new constraints from existing ones,
    creating a more complete and logical set of profile characteristics.
    """
    debug_print_func("Running inference engine...")
    
    # Loop until no new information can be inferred in a full pass
    while True:
        previous_constraints = constraints.copy()
        
        for rule in INFERENCE_RULES:
            constraints = rule(constraints, region_data, debug_print_func)
            
        if constraints == previous_constraints:
            break  # Exit loop if no new constraints were added
            
    debug_print_func(f"Inference complete. Final constraints: {constraints}")
    return constraints
