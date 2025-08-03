import random

def generate_gender(gender_constraint):
    if gender_constraint and gender_constraint != 'any':
        gender = gender_constraint
    else:
        gender = random.choice(['male', 'female'])
    return {'gender': gender}
