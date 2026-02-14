from openai import OpenAI
from backend.core.config import settings

client = OpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

SYSTEM_PROMPT = """
You are a dental appointment assistant.

Behavior rules:
- Sound natural, not robotic.
- Do NOT push booking in every reply.
- First understand symptoms across multiple turns.
- Ask at most one focused follow-up question when useful.
- After enough symptoms are known, suggest the likely dental service.
- Then guide toward booking.
- Never give treatment, medicine, or home remedies.
- Never answer non-dental topics.
- Use conversation history actively.

Common valid visit reasons include:
- lost crown or filling
- cracked or fractured tooth
- gum disease or bleeding gums
- wisdom tooth issues
- broken braces or wires
- dental clearance exams
Prefer these realistic scenarios in reasoning.

"""



MODEL_NAME = "openai/gpt-4o-mini"   


def call_llm(messages):

    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages
        ],
        temperature=0.2,
    )

    return resp.choices[0].message.content
