import re

NIP_PATTERN = re.compile(r"[0-9]{10}")
NIP_WEIGHTS = (6, 5, 7, 2, 3, 4, 5, 6, 7)


def normalize_nip(value: str) -> str:
    return value.replace("-", "").replace(" ", "")


def is_valid_nip(value: str) -> bool:
    digits = normalize_nip(value)
    if not NIP_PATTERN.fullmatch(digits):
        return False
    checksum = sum(
        int(digit) * weight for digit, weight in zip(digits[:9], NIP_WEIGHTS, strict=True)
    )
    control_digit = checksum % 11
    # A remainder of 10 is never used as a control digit, so such a number is invalid.
    return control_digit != 10 and control_digit == int(digits[9])
