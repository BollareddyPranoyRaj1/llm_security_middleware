from typing import Dict
from .policies import SecurityPolicy
from .threat_classifier import ThreatClassifier


class InputValidator:
    def __init__(self, classifier: ThreatClassifier) -> None:
        self.classifier = classifier

    def analyze_input(self, prompt: str, policy: SecurityPolicy) -> Dict[str, str]:
        base = self.classifier.classify(prompt, policy)
        label = base["label"]

        if label == "prompt_injection" and policy.block_injections:
            action = "block"
        elif label == "jailbreak" and policy.block_jailbreaks:
            action = "block"
        else:
            action = "allow"

        base["action"] = action
        return base
