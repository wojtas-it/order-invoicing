NIP_WEIGHTS = (6, 5, 7, 2, 3, 4, 5, 6, 7)
NIP_LENGTH = 10


def normalize_nip(value: str) -> str:
    return value.replace("-", "").replace(" ", "")


def is_valid_nip(value: str) -> bool:
    digits = normalize_nip(value)
    if len(digits) != NIP_LENGTH or not digits.isdigit():
        return False
    checksum = sum(int(digit) * weight for digit, weight in zip(digits, NIP_WEIGHTS, strict=False))
    control_digit = checksum % 11
    return control_digit != 10 and control_digit == int(digits[-1])
