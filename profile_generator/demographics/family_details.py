import random
from rich.prompt import Prompt
from user_input.exceptions import BackException

def generate_marital_status(age, constraints, region_data, province_data, debug_print_func):
    allow_unconventional = constraints.get('allow_unconventional', False)
    legal_marriage_age = region_data.get('legal_marriage_age', 18)

    if age < legal_marriage_age:
        return "Single"

    if allow_unconventional and province_data.get('allows_early_marriage'):
        if random.random() < 0.1: # 10% chance of early marriage
            return 'Married'

    allow_unconventional = constraints.get('allow_unconventional', False)
    legal_marriage_age = region_data.get('legal_marriage_age', 18)

    family_rules = region_data.get('family_details_rules', {})
    marital_status_rules = family_rules.get('marital_status_rules', [])

    selected_rule = None
    for rule in marital_status_rules:
        min_age, max_age = rule['age_range']
        if min_age <= age <= max_age:
            selected_rule = rule
            break

    if selected_rule:
        status_weights = selected_rule['status_weights']
        statuses = list(status_weights.keys())
        weights = list(status_weights.values())
        if sum(weights) > 0:
            return random.choices(statuses, weights=weights, k=1)[0]
        else:
            return "Single" # Fallback
    else:
        return "Single" # Default if no rule matches

def generate_children_info(age, marital_status, constraints, region_data, education_level, debug_print_func):
    allow_unconventional = constraints.get('allow_unconventional', False)
    num_children_constraint = constraints.get('num_children', 'any')

    if age < 16:
        return 0

    if marital_status == "Single" and not allow_unconventional:
        return 0

    if num_children_constraint != 'any':
        debug_print_func(f"generate_children_info - Returning num_children from constraint: {num_children_constraint}")
        return num_children_constraint

    family_rules = region_data.get('family_details_rules', {})
    children_info_rules = family_rules.get('children_info_rules', [])

    num_children = 0
    selected_rule_with_weights = None

    debug_print_func(f"generate_children_info - Age: {age}, Marital Status: {marital_status}, Education Level: {education_level}")

    # First, try to apply rules based on education level and age
    for rule in children_info_rules:
        if "education_level_in" in rule and education_level in rule["education_level_in"]:
            debug_print_func(f"generate_children_info - Checking education-based rule: {rule.get('education_level_in')}")
            for age_rule in rule.get("age_ranges", []):
                min_age, max_age = age_rule['age_range']
                if min_age <= age <= max_age:
                    selected_rule_with_weights = age_rule
                    debug_print_func(f"generate_children_info - Matched education-based age rule: {age_rule['age_range']}")
                    break
            if selected_rule_with_weights:
                break

    # If no education-based rule matched, proceed with marital status rules
    if not selected_rule_with_weights:
        debug_print_func("generate_children_info - No education-based rule matched, checking marital status rules.")
        for rule in children_info_rules:
            if rule.get('marital_status') == marital_status:
                debug_print_func(f"generate_children_info - Checking marital status rule: {rule.get('marital_status')}")
                if marital_status == "Married":
                    for age_rule in rule.get('age_ranges', []):
                        min_age, max_age = age_rule['age_range']
                        if min_age <= age <= max_age:
                            selected_rule_with_weights = age_rule
                            debug_print_func(f"generate_children_info - Matched marital status age rule: {age_rule['age_range']}")
                            break
                else:
                    selected_rule_with_weights = rule
                    debug_print_func(f"generate_children_info - Matched marital status rule (non-married): {rule.get('marital_status')}")
                break

    if selected_rule_with_weights:
        children_weights = selected_rule_with_weights['children_weights']
        debug_print_func(f"generate_children_info - Using children_weights: {children_weights}")
        children_counts = [int(c) for c in children_weights.keys()]
        weights = list(children_weights.values())
        debug_print_func(f"generate_children_info - children_counts: {children_counts}, weights: {weights}")
        if sum(weights) > 0:
            num_children = random.choices(children_counts, weights=weights, k=1)[0]
            debug_print_func(f"generate_children_info - Randomly chosen num_children: {num_children}")
        else:
            num_children = 0 # Fallback
            debug_print_func("generate_children_info - Sum of weights is 0, defaulting to 0 children.")
    else:
        debug_print_func("generate_children_info - No rule matched, defaulting to 0 children.")
        num_children = 0 # Default if no rule matches
    
    # Handle unconventional single parent case if not covered by rules
    if marital_status == "Single" and allow_unconventional and num_children == 0 and random.random() < 0.05:
        num_children = random.choices([0, 1], weights=[0.8, 0.2], k=1)[0]
        debug_print_func(f"generate_children_info - Unconventional single parent case applied, num_children: {num_children}")

    debug_print_func(f"generate_children_info - Final num_children: {num_children}")
    return num_children

def select_family_details(console, max_age, unconventional_data_selection, debug_print_func):
    debug_print_func("Selecting family details.")
    include_family_details = Prompt.ask(
        "[bold green]Do you want to include family details (marital status, children)?[/bold green]",
        choices=["y", "n", "back"],
        default="n",
        console=console
    )
    if include_family_details == "back":
        raise BackException

    marital_status = "any"
    num_children = "any"

    if include_family_details == "y":
        if max_age >= 16: # Assuming 16 is a reasonable minimum age for marital status
            marital_status = Prompt.ask(
                "[bold green]Select marital status:[/bold green]",
                choices=["single", "married", "divorced", "widowed", "any", "back"],
                default="any",
                console=console
            )
            if marital_status == "back":
                raise BackException
            
            if marital_status in ["married", "divorced", "widowed"]:
                num_children = Prompt.ask(
                    "[bold green]Number of children (e.g., '0', '1', '1-3', 'any'):[/bold green]",
                    default="any",
                    console=console
                )
                if num_children == "back":
                    raise BackException
                
                # Basic validation for num_children
                if num_children != "any":
                    if "-" in num_children:
                        try:
                            min_c, max_c = map(int, num_children.split("-"))
                            if min_c < 0 or max_c < min_c:
                                console.print("[yellow]Invalid range for children. Using 'any'.[/yellow]")
                                num_children = "any"
                        except ValueError:
                            console.print("[yellow]Invalid format for children. Using 'any'.[/yellow]")
                            num_children = "any"
                    elif not num_children.isdigit() or int(num_children) < 0:
                        console.print("[yellow]Invalid number of children. Using 'any'.[/yellow]")
                        num_children = "any"
        else:
            console.print("[yellow]Age is too low for marital status and children details. Skipping.[/yellow]")
            include_family_details = "n" # Force to 'n' if age is too low

    return include_family_details == "y", marital_status, num_children