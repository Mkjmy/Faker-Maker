from .inference import run_inference_engine
from .demographics.occupation import determine_occupation

def manage_profile_consistency(constraints, region_data, debug_print_func, apply_consistency_checks):
    """
    Manages the application of consistency checks and inference rules for profile generation.
    Returns the updated constraints and the determined occupation object.
    """
    occupation_obj = None

    if apply_consistency_checks:
        constraints = run_inference_engine(constraints, region_data, debug_print_func)
        profile_for_occupation_determination = {
            'age': constraints.get('age_range', (0, 120))[0], # Use min age for occupation determination
            'gender': constraints.get('gender', 'any')
        }
        # Determine occupation based on inferred constraints
        profile_for_occupation_determination['occupation'], occupation_obj = determine_occupation(
            profile_for_occupation_determination, region_data, debug_print_func, constraints
        )
        # Update constraints with the determined occupation if it was not already set by user
        if not constraints.get('occupation'):
            constraints['occupation'] = profile_for_occupation_determination['occupation']
    else:
        # If consistency checks are off, prioritize user-provided occupation
        if constraints.get('occupation'):
            # Try to find the occupation object for its typical education level
            occupation_obj = next((occ for occ in region_data.get('occupations', {}).get('occupations', []) if occ['name'] == constraints['occupation']), None)
        else:
            # If no user-provided occupation, determine a random one (without inference)
            profile_for_occupation_determination = {
                'age': constraints.get('age_range', (0, 120))[0],
                'gender': constraints.get('gender', 'any')
            }
            profile_for_occupation_determination['occupation'], occupation_obj = determine_occupation(
                profile_for_occupation_determination, region_data, debug_print_func, constraints
            )
            constraints['occupation'] = profile_for_occupation_determination['occupation']

    # Set education level based on user input or determined occupation
    if not apply_consistency_checks and constraints.get('education_level'):
        pass # User's education_level is already in constraints and takes precedence
    else:
        # If consistency checks are on, or no user-provided education_level, use typical education level
        constraints['education_level'] = occupation_obj.get('typical_education_level', "None") if occupation_obj else "None"

    return constraints, occupation_obj
