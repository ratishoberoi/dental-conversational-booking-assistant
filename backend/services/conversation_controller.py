from backend.services.domain_filter import (
    is_dental_query,
    contains_treatment_advice,
)
from backend.services.symptom_mapper import extract_all_services_from_history
from backend.services.doctor_lookup import get_doctors_for_service
from backend.services.scheduler import get_available_slots_for_service
from backend.llm.grok_client import call_llm


# =========================
# Helpers
# =========================


def assistant_question_count(history):
    return sum(
        1 for m in history
        if m["role"] == "assistant" and "?" in m["content"]
    )


def user_wants_booking(text: str) -> bool:
    t = text.lower().strip()
    keywords = [
        "book", "appointment", "schedule",
        "show doctors", "available doctors",
        "yes", "yeah", "yep", "sure",
        "ok", "okay", "go ahead", "please"
    ]
    return any(k in t for k in keywords)


def find_doctor_mentioned(text, doctors):
    t = text.lower()

    for d in doctors:
        full = d["name"].lower()
        parts = full.split()

        if full in t:
            return d

        for p in parts:
            if len(p) >= 4 and p in t:
                return d

    return None


def doctors_already_shown(history):
    return any(
        "available doctors for" in m["content"].lower()
        for m in history
        if m["role"] == "assistant"
    )


def insurance_question_asked(history):
    return any(
        "dental insurance" in m["content"].lower()
        for m in history
        if m["role"] == "assistant"
    )


def slots_already_shown(history):
    return any(
        "available slots with dr." in m["content"].lower()
        for m in history
        if m["role"] == "assistant"
    )


# =========================
# Controller
# =========================


def process_message(history, user_text: str):

    # -------- DOMAIN GUARD --------

    if not is_dental_query(user_text, history):
        return {
            "reply": "I handle only dental appointment conversations.",
            "service": None,
            "slots": []
        }

    service = extract_all_services_from_history(history, user_text)
    q_count = assistant_question_count(history)
    text_l = user_text.lower()

    # -------- STAGE 1 — INTAKE (MAX 3 QUESTIONS) --------

    if q_count < 3 and not doctors_already_shown(history):

        prompt = """
Dental intake assistant.
Ask ONE natural symptom clarification question.
Do NOT repeat facts already stated.
Do NOT mention booking.
Do NOT give treatment advice.
"""

        reply = call_llm(history[-8:] + [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_text},
        ])

        if contains_treatment_advice(reply):
            reply = "I can’t provide treatment guidance, but I can help arrange a dentist visit."

        return {"reply": reply, "service": service, "slots": []}

    # -------- STAGE 2 — TREATMENT ASK → REFUSAL + SPECIALTY + PERMISSION --------

    treatment_words = [
        "treatment", "medicine", "what should i do",
        "how to fix", "how to treat"
    ]

    if service and not doctors_already_shown(history) and any(w in text_l for w in treatment_words):
        return {
            "reply": f"I can’t guide you regarding treatment, but based on your symptoms this is usually handled under {service}. Would you like me to show available doctors for this?",
            "service": service,
            "slots": []
        }

    # -------- STAGE 3 — SPECIALTY EXPLAIN (ONCE) --------

    if service and not doctors_already_shown(history) and not user_wants_booking(user_text):

        prompt = f"""
User likely needs {service}.
Respond with brief empathy.
Explain why this specialty fits in 1–2 lines.
Ask if I should show available doctors.
No treatment advice.
"""

        reply = call_llm(history[-8:] + [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_text},
        ])

        return {"reply": reply, "service": service, "slots": []}

    # -------- STAGE 4 — SHOW DOCTORS (ONLY AFTER CONFIRMATION) --------

    if service and user_wants_booking(user_text) and not doctors_already_shown(history):

        doctors = get_doctors_for_service(service)

        if not doctors:
            return {
                "reply": "No doctors are currently mapped for this service.",
                "service": service,
                "slots": []
            }

        doc_text = "\n".join(
            f"- Dr. {d['name']} — {d['clinic_name']}"
            for d in doctors
        )

        return {
            "reply": f"Available doctors for {service}:\n{doc_text}\n\nWhich doctor would you like to book with?",
            "service": service,
            "doctors": doctors,
            "slots": []
        }

    # -------- STAGE 5 — DOCTOR CHOSEN → INSURANCE GATE --------

    if service and doctors_already_shown(history) and not insurance_question_asked(history):

        doctors = get_doctors_for_service(service)
        chosen = find_doctor_mentioned(user_text, doctors)

        if chosen:
            return {
                "reply": "Before I show slots, may I confirm — do you have dental insurance?",
                "service": service,
                "doctor": chosen,
                "slots": []
            }

    # -------- STAGE 6 — INSURANCE FLOW --------

    if service and insurance_question_asked(history) and not slots_already_shown(history):

        doctors = get_doctors_for_service(service)

        # recover chosen doctor from history
        chosen = None
        for m in history:
            if m["role"] == "user":
                chosen = find_doctor_mentioned(m["content"], doctors) or chosen

        if not chosen:
            return {
                "reply": "Please tell me which doctor you would like to book with from the list above.",
                "service": service,
                "slots": []
            }

        if text_l in ["no", "nope", "none"]:
            slots = get_available_slots_for_service(service, doctor_id=chosen["id"])
            return {
                "reply": f"No problem. Here are available slots with Dr. {chosen['name']}. Select one to confirm booking.",
                "service": service,
                "slots": slots[:5]
            }

        if text_l in ["yes", "yeah", "yep"]:
            return {
                "reply": "Please share your insurance provider name and member/policy ID.",
                "service": service,
                "slots": []
            }

        # assume insurance details provided → continue
        if any(k in text_l for k in ["insurance", "policy", "id", "#"]):
            slots = get_available_slots_for_service(service, doctor_id=chosen["id"])
            return {
                "reply": f"Thanks. Here are available slots with Dr. {chosen['name']}. Select one to confirm booking.",
                "service": service,
                "slots": slots[:5]
            }

    # -------- SAFE DEFAULTS --------

    if doctors_already_shown(history):
        return {
            "reply": "Please tell me which doctor you would like to book with from the list above.",
            "service": service,
            "slots": []
        }

    return {
        "reply": "Would you like me to help you book a dental appointment?",
        "service": service,
        "slots": []
    }
