import os
import questionary
from rich.console import Console
import random

from utils.custom_styles import custom_style
from utils.data_loader import load_region_data
from .generation_mode import select_generation_mode, get_random_constraints
from .region_selection import select_region, select_detailed_location, select_address_input_method, get_manual_address, get_random_detailed_location
from .profile_details import select_num_profiles, select_age_range, select_gender, select_hidden_attributes_inclusion
from .name_method import select_name_generation_method
from .unconventional_data import select_unconventional_data_inclusion
from .family_details import select_family_details
from .physical_details import select_physical_details
from .output_format import select_output_format
from .occupation_details import select_desired_education_level
from .occupation import select_occupation
from .skills_interests import select_skills_interests
from .exceptions import BackException

def get_user_input_generator(regions_config, data_dir, console: Console, debug_print_func, args, is_cli_direct_mode=False):
    """
    Orchestrates the user input process for generating fake profiles using a command-line wizard.
    This function guides the user through a series of questions to gather constraints for profile generation.
    It also handles non-interactive mode by building constraints from command-line arguments.
    """
    # --- Non-Interactive Mode ---
    if args.non_interactive or is_cli_direct_mode:
        debug_print_func("Running in non-interactive mode.")
        
        # (The non-interactive logic remains unchanged)
        constraints = {
            'mode': '2', 'num_profiles': 1, 'region': None, 'age_range': 'any', 'gender': 'any',
            'occupation': 'any', 'marital_status': 'any', 'desired_education_level': 'any',
            'hobbies': [], 'skills': [], 'unconventional_data_selection': [], 'include_unconventional': False,
            'custom_first_name': None, 'custom_last_name': None, 'output_format': 'console',
            'family_details': False, 'physical_details': False, 'include_hidden_attributes': False,
            'name_generation_method': 'existing',
        }
        if args.num_profiles is not None:
            try: constraints['num_profiles'] = int(args.num_profiles)
            except ValueError: debug_print_func(f"Warning: Could not parse num_profiles '{args.num_profiles}'. Using default.")
        if args.region is not None: constraints['region'] = args.region
        if args.age is not None:
            value = args.age
            if isinstance(value, str):
                if '-' in value: parts = value.split('-'); constraints['age_range'] = (int(parts[0]), int(parts[1]))
                elif '+' in value: constraints['age_range'] = (int(value.replace('+', '')), 1000)
                elif value.lower() == 'any': constraints['age_range'] = 'any'
                else:
                    try: age = int(value); constraints['age_range'] = (age, age)
                    except ValueError: debug_print_func(f"Warning: Could not parse age '{value}'. Using default.")
        if args.gender is not None: constraints['gender'] = args.gender
        if args.occupation is not None: constraints['occupation'] = args.occupation
        if args.marital_status is not None: constraints['marital_status'] = args.marital_status; constraints['family_details'] = True
        if args.num_children is not None: constraints['num_children'] = args.num_children; constraints['family_details'] = True
        if args.education_level is not None: constraints['desired_education_level'] = args.education_level
        if args.hobbies is not None: constraints['hobbies'] = [h.strip() for h in args.hobbies.split(',') if h.strip()]; constraints['include_skills_interests'] = True
        if args.skills is not None: constraints['skills'] = [s.strip() for s in args.skills.split(',') if s.strip()]; constraints['include_skills_interests'] = True
        if args.include_unconventional:
            constraints['include_unconventional'] = True
            constraints['unconventional_data_selection'] = ["personality_traits", "life_events", "online_behaviors", "texting_typing_style", "digital_footprint", "device_habits"]
        if args.include_hidden_attributes: constraints['include_hidden_attributes'] = True
        if args.physical_details: constraints['physical_details'] = True
        if args.address_manual_input: constraints['address_input_method'] = 'manual'; constraints['address_manual_input'] = args.address_manual_input
        elif args.location: constraints['address_input_method'] = 'detailed'; constraints['location'] = args.location
        if args.personality_trait is not None:
            constraints['personality_trait'] = args.personality_trait; constraints['include_unconventional'] = True
            if 'personality_traits' not in constraints['unconventional_data_selection']: constraints['unconventional_data_selection'].append('personality_traits')
        if args.exceptionality_score is not None:
            try:
                constraints['exceptionality_score'] = int(args.exceptionality_score); constraints['include_unconventional'] = True
                if 'personality_traits' not in constraints['unconventional_data_selection']: constraints['unconventional_data_selection'].append('personality_traits')
            except ValueError: debug_print_func(f"Warning: Could not parse exceptionality_score '{args.exceptionality_score}'. Ignoring.")
        if args.name is not None:
            if not constraints['custom_first_name'] and not constraints['custom_last_name']:
                name_parts = args.name.split(' ', 1)
                if len(name_parts) > 0: constraints['custom_first_name'] = name_parts[0]
                if len(name_parts) > 1: constraints['custom_last_name'] = name_parts[1]
                constraints['name_generation_method'] = 'custom'
        if args.custom_first_name is not None: constraints['custom_first_name'] = args.custom_first_name; constraints['name_generation_method'] = 'custom'
        if args.custom_last_name is not None: constraints['custom_last_name'] = args.custom_last_name; constraints['name_generation_method'] = 'custom'
        if constraints['custom_first_name'] or constraints['custom_last_name']: constraints['name_generation_method'] = 'custom'
        if constraints['region'] is None: constraints['region'] = random.choice(regions_config)['id']
        debug_print_func(f"Constraints from args (non-interactive): {constraints}")
        return constraints

    # --- Interactive Mode ---
    constraints = {}
    answered_questions = []

    def format_display_answer(question, answer):
        if answer is None:
            return ""
        q_type = question.get('type')
        choices = question.get('choices', [])

        if q_type == 'confirm':
            return "Yes" if answer else "No"

        if q_type in ['select', 'autocomplete']:
            # Handle list of dicts
            if choices and isinstance(choices[0], dict):
                for choice in choices:
                    if choice.get('value') == answer:
                        return choice.get('name', str(answer))
            # Handle list of strings or fallback
            return str(answer) if answer else "Random"

        if q_type == 'checkbox':
            if not answer:
                return "None"
            names = []
            for val in answer:
                found = False
                for c in choices:
                    if isinstance(c, dict) and c.get('value') == val:
                        names.append(c.get('name', str(val)))
                        found = True
                        break
                if not found:
                    names.append(str(val))
            return ", ".join(names)
            
        return str(answer)

    def render_and_ask(question):
        console.clear()
        for qa in answered_questions:
            console.print(f"[dim]? {qa['prompt']} [/][grey50]{qa['answer']}[/]")
        
        answer = None
        q_type = question.get('type')
        
        debug_print_func(f"Asking question: {question.get('prompt')} (type: {q_type})")
        
        try:
            if q_type == 'select': answer = questionary.select(message=question['prompt'], choices=question['choices'], style=custom_style).ask()
            elif q_type == 'text':
                answer = questionary.text(message=question['prompt'], default=question.get('default'), style=custom_style).ask()
                if answer == '': answer = question.get('default', '')
            elif q_type == 'confirm': answer = questionary.confirm(message=question['prompt'], default=question.get('default', False), style=custom_style).ask()
            elif q_type == 'checkbox': answer = questionary.checkbox(message=question['prompt'], choices=question['choices'], style=custom_style).ask()
            elif q_type == 'autocomplete': answer = questionary.autocomplete(message=question['prompt'], choices=question['choices'], default=question.get('default', ''), style=custom_style).ask()
        except KeyboardInterrupt:
            debug_print_func("KeyboardInterrupt caught in render_and_ask. Returning None.")
            return None
        
        if answer is None:
            debug_print_func("Answer is None (likely Ctrl+C). Returning None.")
            return None
        
        print(f"DEBUG: Raw answer from questionary: '{answer}' (type: {type(answer)})") # Added print

        # Handle 'back' action for different question types
        is_back_action = False
        if isinstance(answer, str) and answer.strip().lower() == "back":
            is_back_action = True
        elif isinstance(answer, list) and "back" in [item.lower() if isinstance(item, str) else item for item in answer]:
            is_back_action = True

        print(f"DEBUG: is_back_action evaluated to: {is_back_action}") # Added print
        if is_back_action:
            print(f"DEBUG: Raising BackException for answer: '{answer}'") # Added print
            raise BackException()
        
        display_answer = format_display_answer(question, answer)
        print(f"DEBUG: Formatted answer for display: {display_answer}") # Added print
        return answer

    # --- Wizard Start ---
    # 1. Select Generation Mode
    mode_question = select_generation_mode(console, regions_config, debug_print_func)
    try:
        mode_answer = render_and_ask(mode_question)
    except BackException:
        debug_print_func("BackException caught at mode selection. Exiting wizard.")
        return {} # Exit wizard if 'back' from first question
    
    if mode_answer is None:
        debug_print_func("Mode answer is None. Exiting wizard.")
        return {}
    constraints['mode'] = mode_answer

    if constraints['mode'] == '1': # Completely Random
        console.print("[bold cyan]Generating a completely random profile...[/bold cyan]")
        random_constraints = get_random_constraints(regions_config, debug_print_func)
        constraints.update(random_constraints)
        constraints.setdefault('num_profiles', 1)
        constraints.setdefault('output_format', 'console')
        debug_print_func(f"Random mode selected. Constraints: {constraints}")
        return constraints

    # --- Detailed Generation Mode ---
    console.clear()
    for qa in answered_questions: console.print(f"[dim]? {qa['prompt']} [/][grey50]{qa['answer']}[/]")
    console.print("[bold cyan]Starting detailed profile generation wizard...[/bold cyan]")

    question_functions = [
        select_num_profiles, select_unconventional_data_inclusion, select_skills_interests,
        select_region, select_address_input_method, select_age_range, select_gender,
        select_hidden_attributes_inclusion, select_name_generation_method,
        select_desired_education_level, select_family_details, select_occupation,
        select_physical_details, select_output_format,
    ]
    
    context = {'debug_print_func': debug_print_func, 'regions_config': regions_config}
    
    current_question_index = 0
    while current_question_index < len(question_functions):
        debug_print_func(f"Loop start: current_question_index = {current_question_index}, answered_questions = {answered_questions}")
        func = question_functions[current_question_index]
        func_args = {'debug_print_func': debug_print_func}
        if func == select_region: func_args['regions_config'] = regions_config
        elif func == select_family_details:
            age_range_str = constraints.get('age_range', "0-0")
            max_age = 1000 if age_range_str.lower() == 'any' else int(age_range_str.split('-')[1]) if '-' in age_range_str else int(age_range_str.replace('+', ''))
            func_args.update({'max_age_for_questions': max_age, 'unconventional_data_selection': constraints.get('unconventional_data_selection', {})})
        elif func == select_occupation:
            occupation_data = context.get('region_data', {}).get('occupations', [])
            func_args['occupation_data'] = occupation_data

        question = func(**func_args)
        
        if not question or question.get('type') == 'skipped':
            debug_print_func(f"Question skipped: {question.get('name')}")
            if 'value' in question:
                if isinstance(question.get('value'), dict): constraints.update(question['value'])
                else:
                    key_to_store = question.get('store_as') or question.get('name')
                    if key_to_store: constraints[key_to_store] = question['value']
            current_question_index += 1 # Move to next question if skipped
            continue

        debug_print_func(f"Before asking: current_question_index = {current_question_index}, answered_questions = {answered_questions}")
        try:
            answer = render_and_ask(question)
        except BackException:
            debug_print_func(f"BackException caught for question at index {current_question_index}")
            if current_question_index > 0:
                current_question_index -= 1
                debug_print_func(f"Decrementing index to {current_question_index}")
                if answered_questions: # Only pop if there's something to pop
                    popped_answer = answered_questions.pop()
                    debug_print_func(f"Popped answer: {popped_answer}")
                debug_print_func(f"After BackException: answered_questions = {answered_questions}")
                continue # Go to previous question
            else:
                debug_print_func("Back from first question. Exiting wizard.")
                # User wants to go back from the very first question
                return {} # Exit wizard

        if answer is None: # KeyboardInterrupt
            debug_print_func("KeyboardInterrupt caught. Exiting wizard.")
            return {} # Exit wizard

        debug_print_func(f"Answer received: {answer}")
        
        # Store the answer in constraints
        key_to_store = question.get('store_as') or question.get('name')
        if key_to_store == 'num_profiles':
            try: constraints[key_to_store] = int(answer)
            except ValueError: console.print(f"[bold red]Invalid number: {answer}. Defaulting to 1.[/bold red]"); constraints[key_to_store] = 1
        else:
            constraints[key_to_store] = answer
            # Special handling for unconventional_data_selection
            if key_to_store == 'unconventional_data_selection' and answer:
                constraints['include_unconventional'] = True

        # Add to answered_questions only if it's a valid answer (not 'back')
        display_answer = format_display_answer(question, answer)
        answered_questions.append({'prompt': question['prompt'], 'answer': display_answer})
        debug_print_func(f"After appending to answered_questions: {answered_questions}")

        # Special handling for address_input_method and detailed location
        if key_to_store == 'address_input_method':
            if answer == 'detailed':
                detailed_loc_q_gen = select_detailed_location(context.get('region_data', {}).get('address_data', {}), debug_print_func)
                go_back_from_detailed = False
                # Store the starting index for detailed location questions
                detailed_location_start_index = len(answered_questions) 
                for detailed_q in detailed_loc_q_gen:
                    debug_print_func(f"Before asking detailed: answered_questions = {answered_questions}")
                    try:
                        loc_answer = render_and_ask(detailed_q)
                        if loc_answer is None: return {} # KeyboardInterrupt
                        constraints['location'] = loc_answer
                        # Add detailed location answer to answered_questions
                        answered_questions.append({'prompt': detailed_q['prompt'], 'answer': format_display_answer(detailed_q, loc_answer)})
                        debug_print_func(f"After appending detailed answer: {answered_questions}")
                    except BackException:
                        debug_print_func("BackException caught in detailed location loop.")
                        go_back_from_detailed = True
                        # Remove all detailed location answers from answered_questions
                        while len(answered_questions) > detailed_location_start_index:
                            answered_questions.pop()
                        break # Break inner loop, go back to address_input_method
                if go_back_from_detailed:
                    debug_print_func("Going back from detailed location.")
                    # Decrement index twice: once for the current question, once more to go back to address_input_method
                    current_question_index -= 1
                    if answered_questions: 
                        popped_answer = answered_questions.pop() # Remove the address_input_method answer
                        debug_print_func(f"Popped address_input_method answer: {popped_answer}")
                    debug_print_func(f"After going back from detailed: answered_questions = {answered_questions}")
                    continue # Restart the address_input_method question
            elif answer == 'manual':
                debug_print_func(f"Before asking manual: answered_questions = {answered_questions}")
                try:
                    manual_addr_q = get_manual_address(debug_print_func)
                    addr_answer = render_and_ask(manual_addr_q)
                    if addr_answer is None: return {} # KeyboardInterrupt
                    constraints['address_manual_input'] = addr_answer
                    # Add manual address answer to answered_questions
                    answered_questions.append({'prompt': manual_addr_q['prompt'], 'answer': format_display_answer(manual_addr_q, addr_answer)})
                    debug_print_func(f"After appending manual answer: {answered_questions}")
                except BackException:
                    debug_print_func("BackException caught in manual address input.")
                    current_question_index -= 1 # Go back to address_input_method
                    if answered_questions: 
                        popped_answer = answered_questions.pop() # Remove the address_input_method answer
                        debug_print_func(f"Popped manual address answer: {popped_answer}")
                    debug_print_func(f"After going back from manual: answered_questions = {answered_questions}")
                    continue # Restart the address_input_method question
        
        current_question_index += 1 # Move to next question

    return constraints