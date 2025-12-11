from typing import Dict, Any
from .policies import SecurityPolicy
from .threat_classifier import ThreatClassifier


class OutputValidator:
    def __init__(self, classifier: ThreatClassifier) -> None:
        self.classifier = classifier

    def analyze_output(self, response: str, policy: SecurityPolicy) -> Dict[str, Any]:
        base = self.classifier.classify(response, policy)
        label = base["label"]

        if label in ("prompt_injection", "jailbreak") and policy.block_sensitive_leaks:
            action = "review"
        else:
            action = "allow"

        base["action"] = action
        return base
