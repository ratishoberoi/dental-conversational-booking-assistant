DENTAL_KEYWORDS = [
    "tooth", "teeth", "gum", "gums",
    "crown", "filling", "root canal",
    "dentist", "dental", "brace", "braces",
    "jaw", "molar", "incisor", "bleeding gums",
    "sensitivity", "toothache", "extraction",
    "implant", "orthodont", "periodontal"
]


def is_dental_query(text: str, history=None):
    t = text.lower()

    if any(k in t for k in DENTAL_KEYWORDS):
        return True

    # allow continuation if prior turns were dental
    if history:
        joined = " ".join(m["content"].lower() for m in history)
        if any(k in joined for k in DENTAL_KEYWORDS):
            return True

    return False


TREATMENT_WORDS = [
    "take this medicine",
    "take ibuprofen",
    "dosage",
    "mg",
    "tablet",
    "drug",
]


def contains_treatment_advice(text: str):
    t = text.lower()
    return any(k in t for k in TREATMENT_WORDS)
