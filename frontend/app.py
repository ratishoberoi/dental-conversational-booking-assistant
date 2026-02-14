import streamlit as st
import requests

CHAT_API = "http://127.0.0.1:8000/chat/chat"
BOOK_API = "http://127.0.0.1:8000/booking/book"
LOGIN_API = "http://127.0.0.1:8000/auth/login"

st.set_page_config(page_title="Dental AI Assistant", layout="wide")
st.title("Dental Conversational Booking Assistant")

# ---------------- SESSION STATE ----------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "token" not in st.session_state:
    st.session_state.token = ""

if "last_slots" not in st.session_state:
    st.session_state.last_slots = []

if "last_service" not in st.session_state:
    st.session_state.last_service = None

# ---------------- LOGIN PANEL ----------------

with st.expander("Login for Booking", expanded=False):

    email = st.text_input("Email")
    pw = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            r = requests.post(
                LOGIN_API,
                json={"email": email, "password": pw},
                timeout=15
            )
            if r.status_code == 200:
                st.session_state.token = r.json()["token"]
                st.success("Login successful")
            else:
                st.error("Invalid credentials")
        except Exception:
            st.error("Login API not reachable")

# ---------------- RENDER CHAT ----------------

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- USER INPUT ----------------

user_input = st.chat_input("Describe your dental issue...")

if user_input:

    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    payload = {
        "history": st.session_state.chat_history,
        "message": user_input
    }

    try:
        r = requests.post(CHAT_API, json=payload, timeout=30)
        data = r.json()
    except Exception:
        data = {
            "reply": "Backend not reachable. Ensure API server is running.",
            "slots": [],
            "service": None
        }

    reply = data["reply"]

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": reply
    })

    with st.chat_message("assistant"):
        st.markdown(reply)

    # persist slots for button clicks across reruns
    st.session_state.last_slots = data.get("slots") or []
    st.session_state.last_service = data.get("service")

# ---------------- SLOT SECTION (STAGE GATED BY BACKEND) ----------------

if st.session_state.last_slots:

    st.markdown("### Available Appointment Slots")

    for s in st.session_state.last_slots:

        label = f"{s.get('doctor_name','Doctor')} — {s['time']}"


        if st.button(label, key=f"slot_{s['slot_id']}"):

            if not st.session_state.token:
                st.error("Please login first to book.")
            else:
                try:
                    resp = requests.post(
                        BOOK_API,
                        params={
                            "slot_id": s["slot_id"],
                            "service_name": st.session_state.last_service or "General Dentistry"
                        },
                        headers={
                            "Authorization": f"Bearer {st.session_state.token}"
                        },
                        timeout=20
                    )

                    if resp.status_code == 200:
    
                        confirm_msg = f"""
                    ### ✅ Appointment Confirmed

                    **Doctor ID:** {s['doctor_name']}  
                    **Time:** {s['time']}  
                    **Service:** {st.session_state.last_service or "General Dentistry"}

                    Please arrive 10 minutes early.
                    """

                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": confirm_msg
                        })

                        st.success(confirm_msg)

                        # clear slots after booking
                        st.session_state.last_slots = []

                        st.rerun()


                    else:
                        st.error("Slot already booked or invalid")

                except Exception:
                    st.error("Booking API error")
