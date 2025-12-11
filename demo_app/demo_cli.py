# demo_app/demo_cli.py
from typing import Any
from src.middleware import LLMSecurityMiddleware, BALANCED_POLICY


def fake_llm_client(prompt: str, **_: Any) -> str:
    # Dummy stand‑in for a real LLM call
    return f"[LLM RESPONSE] You said: {prompt}"


def main() -> None:
    middleware = LLMSecurityMiddleware(
        base_llm_client=fake_llm_client,
        policy=BALANCED_POLICY,
    )

    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input.strip():
            continue

        response = middleware.generate(user_input)
        print("Model:", response)


if __name__ == "__main__":
    main()
