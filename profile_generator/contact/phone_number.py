import random

def generate_phone_number(region_data, age, hidden_attributes):
    min_phone_age = region_data.get('email_rules', {}).get('age_limits', {}).get('min_phone_age', 18) # Default to 18 if not found
    phone_number = None

    if age is not None and isinstance(age, int) and age >= min_phone_age:
        if 'phone_number_formats' in region_data and region_data['phone_number_formats']:
            phone_format = random.choice(region_data['phone_number_formats'])
            phone_number_str = ""
            for char in phone_format:
                if char == '#':
                    phone_number_str += str(random.randint(0, 9))
                else:
                    phone_number_str += char
            phone_number = phone_number_str.replace(" ", "") # Remove spaces for cleaner output
    
    return {'phone_number': phone_number}
