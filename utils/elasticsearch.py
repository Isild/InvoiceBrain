

def validate_sort_fields(fields_to_check: list[str], allowed_fields: list[str]) -> bool:
    allowed_fields = set(allowed_fields)
    invalid_fields = [
        field for field in fields_to_check
        if field.replace(" ", "") not in allowed_fields
    ]

    if invalid_fields:
        return False

    return True
