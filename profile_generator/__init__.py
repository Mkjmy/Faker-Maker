from .core.name import generate_name
from .core.age_dob import generate_age_and_dob
from .core.gender import generate_gender
from .location_generator import generate_address
from .contact.phone_number import generate_phone_number
from .demographics.occupation import generate_occupation
from .email_generation.email_generator import generate_email
from .physical.physical_description import generate_physical_description
from .demographics.hobbies import generate_hobbies_interests
from .demographics.skills_interests import generate_skills_interests

# Import unconventional data generators
from .unconventional.unconventional_data import generate_unconventional_data, generate_hidden_attributes

def generate_fake_personal_info(region_data, constraints, debug_print_func, apply_consistency_checks=False):
    """Generates a complete fake personal profile based on constraints."""
    profile = {}

    # 1. Core Attributes (independent of hidden attributes)
    profile.update(generate_name(region_data, constraints.get('gender'), constraints.get('name_method'), constraints.get('custom_first_name'), constraints.get('custom_last_name')))
    profile.update(generate_age_and_dob({'age_range': constraints.get('age_range')}))
    profile.update(generate_gender(constraints.get('gender')))
    profile.update(generate_address(region_data, constraints.get('region')))

    # Add region_id to region_data for email generation (already done, keep it here)
    region_data['region_id'] = constraints.get('region')

    # 2. Generate Hidden Attributes (based on core attributes and constraints)
    # These are the "nội tại bên trong" that will influence other generations
    hidden_attributes = generate_hidden_attributes(
        unconventional_data_rules=region_data['unconventional_data_rules'],
        profile=profile, # Pass current profile for age/gender context if needed by hidden_attributes generation
        constraints=constraints,
        debug_print_func=debug_print_func,
        skills_interests_rules=region_data.get('skills_interests_rules'),
        region_data=region_data # Pass region_data for location biases
    )
    profile.update(hidden_attributes) # Add all generated hidden attributes to the profile

    # 3. Generate other attributes, influenced by hidden_attributes
    profile.update(generate_occupation(region_data, profile.get('age'), constraints.get('occupation'), hidden_attributes))
    profile.update(generate_email(profile, region_data, constraints, hidden_attributes)) # Pass hidden_attributes
    profile.update(generate_phone_number(region_data, profile.get('age'), hidden_attributes)) # Pass hidden_attributes
    profile.update(generate_physical_description(region_data, profile.get('gender'), profile.get('age'), hidden_attributes, debug_print_func)) # Pass hidden_attributes

    # Unconventional Data (now always generated if selected, influenced by hidden_attributes)
    if constraints.get('include_unconventional'):
        unconventional_choices = {
            key: key in constraints.get('unconventional_data_selection', []) for key in [
                'personality_traits', 'life_events', 'online_behaviors',
                'texting_typing_style', 'digital_footprint', 'device_habits'
            ]
        }
        # personality_traits is already handled by generate_hidden_attributes, so we might want to exclude it here
        # or ensure generate_unconventional_data handles it gracefully.
        # For now, let's assume generate_unconventional_data will only generate the *other* unconventional data.
        if any(unconventional_choices.values()):
            unconventional_data_generated = generate_unconventional_data(
                unconventional_data_rules=region_data['unconventional_data_rules'],
                age=profile.get('age'),
                unconventional_data_selection=unconventional_choices,
                hidden_attributes=hidden_attributes, # Pass the generated hidden_attributes
                debug_print_func=debug_print_func
            )
            profile.update(unconventional_data_generated)

    # Hobbies and Skills (now influenced by hidden_attributes)
    if constraints.get('include_skills_interests'): # Assuming a constraint for this
        skills, interests = generate_skills_interests(
            age=profile.get('age'),
            skills_interests_rules=region_data.get('skills_interests_rules'),
            profile=profile, # Pass profile for context if needed
            personality_trait=hidden_attributes.get('personality_trait'), # Pass specific hidden attribute
            debug_print_func=debug_print_func,
            hidden_attributes=hidden_attributes # Pass all hidden attributes
        )
        profile['skills'] = skills
        profile['interests'] = interests
        # Also generate hobbies, which might be influenced by hidden attributes
        hobbies = generate_hobbies_interests(
            age=profile.get('age'),
            region_data=region_data,
            profile=profile, # Pass profile for context if needed
            personality_trait=hidden_attributes.get('personality_trait'), # Pass specific hidden attribute
            debug_print_func=debug_print_func,
            hidden_attributes=hidden_attributes # Pass all hidden attributes
        )
        profile['hobbies'] = hobbies


    return profile