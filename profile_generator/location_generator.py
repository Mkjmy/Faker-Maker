import random

def get_random_location(region_data, constraints):
    location_constraints = constraints.get('location', {})
    
    regions = region_data.get('address_data', {}).get('regions', [])
    if not regions:
        return "Unknown Address", "Unknown Location", None

    selected_region = None
    if location_constraints.get('region'):
        selected_region = next((r for r in regions if r['name'] == location_constraints['region']), None)
    if not selected_region: # If constrained region not found or no constraint, pick randomly
        if regions:
            selected_region = random.choice(regions)
        else:
            return "Unknown Address", "Unknown Location", None # Should not happen due to initial check

    # Initialize address parts
    address_parts = []
    city_name = "Unknown Location" # Initialize city_name
    selected_province_obj = None

    # Process Region
    if selected_region:
        address_parts.append(selected_region['name'])

        # Process Province/State
        provinces = selected_region.get('provinces', []) or \
                    selected_region.get('states', []) or \
                    selected_region.get('counties', []) or \
                    selected_region.get('principal_areas', []) or \
                    selected_region.get('districts', []) or \
                    selected_region.get('regions', []) # Fallback for regions within regions

        selected_province = None
        if location_constraints.get('province'):
            selected_province = next((p for p in provinces if p['name'] == location_constraints['province']), None)
        if not selected_province:
            if provinces:
                selected_province = random.choice(provinces)
        
        if selected_province:
            address_parts.insert(0, f"{selected_province.get('type', '')} {selected_province.get('name', '')}".strip())
            selected_province_obj = selected_province

            # Process District/Administrative Unit
            districts = selected_province.get('administrative_units', [])
            selected_admin_unit = None
            if location_constraints.get('district'):
                selected_admin_unit = next((d for d in districts if d['name'] == location_constraints['district']), None)
            if not selected_admin_unit:
                if districts:
                    selected_admin_unit = random.choice(districts)
            
            if selected_admin_unit:
                address_parts.insert(0, f"{selected_admin_unit.get('type', '')} {selected_admin_unit.get('name', '')}".strip())
                city_name = selected_admin_unit['name'] # Store the city name here

                # Process Commune/Sub-unit
                communes = selected_admin_unit.get('sub_units', [])
                selected_sub_unit = None
                if location_constraints.get('commune'):
                    selected_sub_unit = next((c for c in communes if c['name'] == location_constraints['commune']), None)
                if not selected_sub_unit:
                    if communes:
                        selected_sub_unit = random.choice(communes)
                
                if selected_sub_unit:
                    address_parts.insert(0, f"{selected_sub_unit.get('type', '')} {selected_sub_unit.get('name', '')}".strip())

                    # Handle nested sub_units for streets
                    final_level_unit = selected_sub_unit
                    if 'sub_units' in selected_sub_unit and selected_sub_unit['sub_units']:
                        final_level_unit = random.choice(selected_sub_unit['sub_units'])
                        address_parts.insert(0, f"{final_level_unit.get('type', '')} {final_level_unit.get('name', '')}".strip())

                    # Process Streets
                    streets = final_level_unit.get('streets', [])
                    if streets:
                        selected_street = random.choice(streets)
                        street_number = random.randint(1, 999)
                        address_parts.insert(0, f"{street_number} {selected_street['name']}")
                        # location_name remains the deepest unit with streets

    # Filter out empty strings and join
    final_address = ", ".join(filter(None, address_parts))
    if not final_address:
        return "Unknown Address", "Unknown Location", None # Fallback if nothing could be generated

    return final_address, city_name, selected_province_obj

def generate_address(region_data, region_id):
    """Wrapper function to generate just the address string."""
    # We pass an empty constraints dict because we are not constraining location here
    address, _, _ = get_random_location(region_data, {})
    return {"Address": address}
