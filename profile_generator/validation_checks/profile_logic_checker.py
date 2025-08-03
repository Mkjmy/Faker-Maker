
from datetime import datetime

# Helper function to handle checks that can be overridden by exceptionality
def _handle_exceptional_check(errors: list, condition: bool, exceptionality_score: int, exceptional_threshold: int, error_msg: str, warning_msg: str):
    """
    Adds an error or a warning to the list based on a condition and the exceptionality score.
    """
    if condition:
        if exceptionality_score < exceptional_threshold:
            errors.append(f"Error: {error_msg}")
        else:
            errors.append(f"Warning: {warning_msg}")

def check_profile_logic(profile: dict, debug_print_func) -> list[str]:
    errors = []
    # Standardize profile keys to lowercase for case-insensitive access
    p = {k.lower(): v for k, v in profile.items()}

    # Lấy dữ liệu từ profile đã chuẩn hóa, xử lý trường hợp thiếu key
    age = p.get('age')
    dob_str = p.get('dob')
    education_index = p.get('educationindex')
    education_level = p.get('education level')
    occupation = p.get('occupation')
    skills = p.get('skills', [])
    marital_status = p.get('marital_status')
    physical_desc = p.get('physical description', {})
    personality_trait = p.get('personalitytrait')
    life_events = p.get('lifeevents', [])
    online_behavior = p.get('onlinebehavior')
    texting_typing = p.get('textingtyping')
    culture_exposure_level = p.get('cultureexposurelevel')
    digital_native_score = p.get('digitalnativescore')
    geo_mobility_index = p.get('geomobilityindex')
    internal_consistency = p.get('internalconsistency')
    self_memory_accuracy = p.get('selfmemoryaccuracy')
    exceptionality_score = p.get('exceptionalityscore', 0)
    email = p.get('email')

    # Ngưỡng cho tài năng/đặc biệt
    exceptional_threshold = 80
    low_self_memory_threshold = 30

    # 1. Kiểm tra Tuổi không khớp với ngày sinh (Dob)
    if isinstance(age, int) and isinstance(dob_str, str):
        try:
            dob_date = datetime.strptime(dob_str, '%Y-%m-%d')
            today = datetime.today()
            calculated_age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
            if abs(calculated_age - age) > 1: # Allow for a 1-year discrepancy
                errors.append(f"Error: Tuổi ({age}) không khớp với ngày sinh ({dob_str}). Tuổi tính toán: {calculated_age}.")
        except (ValueError, TypeError):
            errors.append(f"Error: Định dạng ngày sinh không hợp lệ: {dob_str}. Phải là YYYY-MM-DD.")

    # 2. Kiểm tra Tuổi nhỏ nhưng học vấn cao bất thường
    if isinstance(age, int) and isinstance(education_index, int):
        _handle_exceptional_check(
            errors,
            age < 18 and education_index > 12, # 12 = tốt nghiệp phổ thông
            exceptionality_score, exceptional_threshold,
            f"Tuổi ({age}) quá nhỏ nhưng EducationIndex ({education_index}) quá cao (trên phổ thông).",
            f"Tuổi ({age}) nhỏ nhưng EducationIndex ({education_index}) cao (có thể là tài năng)."
        )
        _handle_exceptional_check(
            errors,
            age < 22 and education_index > 16, # 16 = đại học
            exceptionality_score, exceptional_threshold,
            f"Tuổi ({age}) quá nhỏ nhưng EducationIndex ({education_index}) quá cao (trên đại học).",
            f"Tuổi ({age}) nhỏ nhưng EducationIndex ({education_index}) cao (có thể là tài năng)."
        )

    # 3. Kiểm tra Sự kiện đời sống không phù hợp với tuổi
    if isinstance(age, int) and isinstance(life_events, list):
        _handle_exceptional_check(
            errors,
            "Started a business" in life_events and age < 18,
            exceptionality_score, exceptional_threshold,
            f"'Started a business' ở tuổi quá trẻ ({age}).",
            f"'Started a business' ở tuổi trẻ ({age}) (có thể là tài năng)."
        )
        if "Had first child" in life_events and age < 16:
            errors.append(f"Error: 'Had first child' ở tuổi quá trẻ ({age}).")
        if "Became a grandparent" in life_events and age < 40:
            errors.append(f"Error: 'Became a grandparent' ở tuổi quá trẻ ({age}).")

    # 4. Kiểm tra Tính cách mâu thuẫn với hành vi trực tuyến
    if isinstance(personality_trait, str) and isinstance(online_behavior, str):
        reserved_creator = personality_trait == "Reserved" and online_behavior == "Content creator"
        energetic_lurker = personality_trait == "Energetic" and online_behavior == "Lurker"
        if reserved_creator or energetic_lurker:
            if self_memory_accuracy is not None and self_memory_accuracy < low_self_memory_threshold:
                errors.append(f"Warning: Tính cách '{personality_trait}' mâu thuẫn với hành vi trực tuyến '{online_behavior}' (có thể do SelfMemoryAccuracy thấp).")
            else:
                errors.append(f"Error: Tính cách '{personality_trait}' mâu thuẫn với hành vi trực tuyến '{online_behavior}'.")

    # 5. Kiểm tra Người già nhưng DigitalNativeScore quá cao
    if isinstance(age, int) and isinstance(digital_native_score, int):
        _handle_exceptional_check(
            errors,
            age >= 65 and digital_native_score > 70,
            exceptionality_score, exceptional_threshold,
            f"Người già ({age} tuổi) nhưng DigitalNativeScore ({digital_native_score}) quá cao.",
            f"Người già ({age} tuổi) nhưng DigitalNativeScore ({digital_native_score}) cao (có thể là tài năng)."
        )

    # 6. Cảnh báo InternalConsistency thấp
    if isinstance(internal_consistency, int) and internal_consistency < 20:
        errors.append(f"Warning: InternalConsistency ({internal_consistency}) rất thấp, có thể hồ sơ không nhất quán.")

    # 7. Kiểm tra Nghề nghiệp và Trình độ học vấn (EducationIndex)
    if isinstance(occupation, str) and isinstance(education_index, int):
        high_education_jobs = ["Doctor", "Lawyer", "Engineer", "Scientist", "Professor"]
        _handle_exceptional_check(
            errors,
            occupation in high_education_jobs and education_index < 16,
            exceptionality_score, exceptional_threshold,
            f"Nghề nghiệp ({occupation}) yêu cầu học vấn cao nhưng EducationIndex ({education_index}) thấp.",
            f"Nghề nghiệp ({occupation}) yêu cầu học vấn cao nhưng EducationIndex ({education_index}) thấp (có thể là tài năng)."
        )
        _handle_exceptional_check(
            errors,
            education_index < 12 and occupation in high_education_jobs,
            exceptionality_score, exceptional_threshold,
            f"EducationIndex ({education_index}) quá thấp nhưng nghề nghiệp ({occupation}) yêu cầu cao.",
            f"EducationIndex ({education_index}) thấp nhưng nghề nghiệp ({occupation}) cao (có thể là tài năng)."
        )

    # 8. Kiểm tra Tuổi và Nghề nghiệp
    if isinstance(age, int) and isinstance(occupation, str):
        if occupation == "Student" and age > 35:
            errors.append(f"Warning: Nghề nghiệp 'Student' nhưng tuổi ({age}) khá cao (có thể là học viên cao học/nghiên cứu sinh).")
        experienced_jobs = ["CEO", "Senior Manager", "Director", "Chief Engineer"]
        _handle_exceptional_check(
            errors,
            occupation in experienced_jobs and age < 30,
            exceptionality_score, exceptional_threshold,
            f"Nghề nghiệp ({occupation}) yêu cầu kinh nghiệm nhưng tuổi ({age}) quá trẻ.",
            f"Nghề nghiệp ({occupation}) yêu cầu kinh nghiệm nhưng tuổi ({age}) trẻ (có thể là tài năng)."
        )

    # 9. Kiểm tra DigitalNativeScore và Kiểu gõ tin nhắn (TextingTyping)
    if isinstance(digital_native_score, int) and isinstance(texting_typing, str):
        is_mismatch = digital_native_score < 30 and ("emojis heavily" in texting_typing or "internet slang" in texting_typing)
        if is_mismatch:
            if self_memory_accuracy is not None and self_memory_accuracy < low_self_memory_threshold:
                errors.append(f"Warning: DigitalNativeScore ({digital_native_score}) thấp nhưng kiểu gõ tin nhắn ({texting_typing}) thể hiện kỹ năng số cao (có thể do SelfMemoryAccuracy thấp).")
            else:
                errors.append(f"Error: DigitalNativeScore ({digital_native_score}) thấp nhưng kiểu gõ tin nhắn ({texting_typing}) thể hiện kỹ năng số cao.")

    # 10. Kiểm tra CultureExposureLevel và GeoMobilityIndex
    if isinstance(culture_exposure_level, int) and isinstance(geo_mobility_index, int):
        is_mismatch = culture_exposure_level > 70 and geo_mobility_index < 30
        if is_mismatch:
            if self_memory_accuracy is not None and self_memory_accuracy < low_self_memory_threshold:
                errors.append(f"Warning: CultureExposureLevel ({culture_exposure_level}) cao nhưng GeoMobilityIndex ({geo_mobility_index}) thấp (có thể do SelfMemoryAccuracy thấp).")
            else:
                errors.append(f"Error: CultureExposureLevel ({culture_exposure_level}) cao nhưng GeoMobilityIndex ({geo_mobility_index}) thấp.")

    # 11. Kiểm tra Email cho người quá già hoặc quá trẻ
    if isinstance(age, int) and email is not None:
        if age < 13:
            errors.append(f"Warning: Người quá trẻ ({age} tuổi) có email ({email}). Thường do phụ huynh tạo.")
        elif age > 90:
            errors.append(f"Warning: Người quá già ({age} tuổi) có email ({email}).")

    # === NEW LOGIC CHECKS ===

    # 12. Kiểm tra Nghề nghiệp và Kỹ năng
    if isinstance(occupation, str) and isinstance(skills, list) and skills:
        skill_requirements = {
            "Engineer": ["engineering", "mathematics", "physics", "problem-solving"],
            "Software Developer": ["programming", "debugging", "system design", "git"],
            "Doctor": ["medicine", "biology", "anatomy", "patient care"],
            "Accountant": ["accounting", "bookkeeping", "financial analysis", "excel"]
        }
        required_skills = skill_requirements.get(occupation)
        if required_skills and not any(skill in skills for skill in required_skills):
            errors.append(f"Warning: Nghề nghiệp '{occupation}' nhưng thiếu các kỹ năng cơ bản liên quan (ví dụ: {', '.join(required_skills[:2])}).")

    # 13. Kiểm tra Tình trạng hôn nhân và Tuổi
    if isinstance(age, int) and isinstance(marital_status, str):
        if age < 16 and marital_status in ["married", "divorced", "widowed"]:
            errors.append(f"Error: Tình trạng hôn nhân '{marital_status}' không hợp lệ cho tuổi ({age}).")
        elif age < 18 and marital_status in ["divorced", "widowed"]:
            errors.append(f"Warning: Tình trạng hôn nhân '{marital_status}' bất thường cho tuổi ({age}).")

    # 14. Kiểm tra Ngoại hình và Tuổi
    if isinstance(age, int) and isinstance(physical_desc, dict):
        hair_color = physical_desc.get('hair_color', '').lower()
        if age < 30 and 'grey' in hair_color:
            _handle_exceptional_check(
                errors,
                True,
                exceptionality_score, exceptional_threshold,
                f"Có tóc bạc ('{hair_color}') ở tuổi ({age}) quá trẻ.",
                f"Có tóc bạc ('{hair_color}') ở tuổi ({age}) trẻ (có thể do di truyền/bệnh lý)."
            )

    # 15. Kiểm tra Cấp độ học vấn và Chỉ số học vấn
    if isinstance(education_level, str) and isinstance(education_index, int):
        education_map = {
            "high school": (10, 12),
            "associates": (13, 14),
            "bachelors": (15, 16),
            "masters": (17, 18),
            "doctorate": (19, 22)
        }
        expected_range = education_map.get(education_level.lower())
        if expected_range and not (expected_range[0] <= education_index <= expected_range[1]):
            errors.append(f"Error: Cấp độ học vấn '{education_level}' không khớp với EducationIndex ({education_index}). Mong đợi trong khoảng {expected_range}.")

    return errors