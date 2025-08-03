import random

def generate_age_and_dob(constraints):
    age_range_str = constraints.get('age_range', 'any')

    if isinstance(age_range_str, str) and age_range_str.lower() == 'any':
        min_age = 18
        max_age = 99
    elif isinstance(age_range_str, tuple):
        min_age, max_age = age_range_str
    elif isinstance(age_range_str, str) and '-' in age_range_str:
        min_age_str, max_age_str = age_range_str.split('-')
        min_age = int(min_age_str)
        max_age = int(max_age_str)
    elif isinstance(age_range_str, str) and '+' in age_range_str:
        min_age = int(age_range_str.replace('+', ''))
        max_age = 99 # Assume a reasonable upper limit for 'X+'
    elif isinstance(age_range_str, str):
        min_age = int(age_range_str)
        max_age = int(age_range_str)

    age = random.randint(min_age, max_age)
    birth_year = 2025 - age
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28) # Simple approach for now
    dob = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
    return {'age': age, 'dob': dob}
