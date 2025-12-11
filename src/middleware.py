from typing import Any, Callable, Dict, Optional
from .policies import SecurityPolicy, BALANCED_POLICY
from .threat_classifier import ThreatClassifier
from .input_validator import InputValidator
from .output_validator import OutputValidator
from .logger import SecurityLogger


class LLMSecurityMiddleware:
    def __init__(
        self,
        base_llm_client: Callable[..., str],
        policy: SecurityPolicy = BALANCED_POLICY,
        logger: Optional[SecurityLogger] = None,
    ) -> None:
        self.base_llm_client = base_llm_client
        self.policy = policy
        self.classifier = ThreatClassifier()
        self.input_validator = InputValidator(self.classifier)
        self.output_validator = OutputValidator(self.classifier)
        self.logger = logger or SecurityLogger()

    def generate(self, prompt: str, **kwargs: Any) -> str:
        input_result = self.input_validator.analyze_input(prompt, self.policy)
        input_label = input_result.get("label", "safe")
        input_reason = input_result.get("reason", "")
        input_action = input_result.get("action", "allow")

        self.logger.log_event(
            event_type="input",
            text=prompt,
            label=input_label,
            reason=input_reason,
            action=input_action,
        )

        if input_action == "block":
            return "Request blocked by security policy."

        raw_response = self.base_llm_client(prompt, **kwargs)

        output_result = self.output_validator.analyze_output(raw_response, self.policy)
        output_label = output_result.get("label", "safe")
        output_reason = output_result.get("reason", "")
        output_action = output_result.get("action", "allow")

        self.logger.log_event(
            event_type="output",
            text=raw_response,
            label=output_label,
            reason=output_reason,
            action=output_action,
        )

        return raw_response
