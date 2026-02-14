# -------- Canonical services --------

SYMPTOM_SERVICE_MAP = {

    # -------- General Dentistry --------
    "tooth pain": "General Dentistry",
    "toothache": "General Dentistry",
    "sensitivity": "General Dentistry",
    "checkup": "General Dentistry",
    "dental exam": "General Dentistry",
    "clearance": "General Dentistry",
    "bad breath": "General Dentistry",

    # -------- Restorative --------
    "crown": "Restorative Dentistry",
    "crown came off": "Restorative Dentistry",
    "lost crown": "Restorative Dentistry",
    "filling": "Restorative Dentistry",
    "lost filling": "Restorative Dentistry",
    "cracked tooth": "Restorative Dentistry",
    "broken tooth": "Restorative Dentistry",
    "chipped tooth": "Restorative Dentistry",
    "hole in tooth": "Restorative Dentistry",
    "cavity": "Restorative Dentistry",
    "bit something hard": "Restorative Dentistry",

    # -------- Endodontics --------
    "deep pain": "Endodontics",
    "nerve pain": "Endodontics",
    "root canal": "Endodontics",
    "throbbing tooth": "Endodontics",
    "pain at night": "Endodontics",

    # -------- Periodontal --------
    "bleeding gums": "Periodontal Care",
    "swollen gums": "Periodontal Care",
    "gum pain": "Periodontal Care",
    "gum infection": "Periodontal Care",
    "deep cleaning": "Periodontal Care",
    "receding gums": "Periodontal Care",

    # -------- Orthodontics --------
    "braces": "Orthodontics",
    "wire": "Orthodontics",
    "broken wire": "Orthodontics",
    "crooked teeth": "Orthodontics",
    "alignment": "Orthodontics",
    "retainer": "Orthodontics",

    # -------- Oral Surgery --------
    "wisdom tooth": "Oral Surgery",
    "impacted tooth": "Oral Surgery",
    "extraction": "Oral Surgery",
    "remove tooth": "Oral Surgery",
    "swelling jaw": "Oral Surgery",
    "cannot open mouth": "Oral Surgery",
}


# -------- mapper --------

def extract_all_services_from_history(history, new_text):

    text = " ".join(
        m["content"] for m in history if m["role"] == "user"
    ) + " " + new_text

    t = text.lower()

    matches = []

    for k, v in SYMPTOM_SERVICE_MAP.items():
        if k in t:
            matches.append(v)

    if not matches:
        return None

    # most frequent match wins
    return max(set(matches), key=matches.count)
