from dataclasses import dataclass


@dataclass
class SecurityPolicy:
    name: str
    strictness_level: int  # 1 = lenient, 2 = balanced, 3 = strict
    block_injections: bool = True
    block_jailbreaks: bool = True
    block_sensitive_leaks: bool = True


STRICT_POLICY = SecurityPolicy(
    name="strict",
    strictness_level=3,
    block_injections=True,
    block_jailbreaks=True,
    block_sensitive_leaks=True,
)

BALANCED_POLICY = SecurityPolicy(
    name="balanced",
    strictness_level=2,
    block_injections=True,
    block_jailbreaks=True,
    block_sensitive_leaks=True,
)
