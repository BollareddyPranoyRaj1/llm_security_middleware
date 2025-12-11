# LLM Security Middleware Evaluation Report

## 1. Overview

This document describes the evaluation of a rule-based security middleware for large language model (LLM) applications. The middleware is designed to detect and mitigate prompt injection, jailbreak attempts, and sensitive-information leakage at the input/output layer, acting as a reusable guardrail between users and an LLM-powered backend. 

The current version focuses on lightweight, explainable keyword-based detection with structured logging, intended as a baseline defense that can be extended with more advanced classifiers in the future.

## 2. System architecture

The middleware is implemented as a Python library with the following core components: 

- **ThreatClassifier** (`src/threat_classifier.py`): Applies keyword-based rules to label text as `safe`, `prompt_injection`, or `jailbreak`, with a short explanation of the matched pattern. 
- **InputValidator** (`src/input_validator.py`): Uses the classifier output plus the active `SecurityPolicy` to decide an action (`allow` or `block`) for user prompts before they reach the LLM. 
- **OutputValidator** (`src/output_validator.py`): Reuses the classifier to analyze LLM responses and mark them as `allow` or `review`, supporting future checks for sensitive content.  
- **LLMSecurityMiddleware** (`src/middleware.py`): Wraps a base LLM client, runs input validation and logging before the call, then output validation and logging after the call, and enforces blocking behavior when required. 
- **SecurityPolicy** (`src/policies.py`): Encodes policy options like `block_injections`, `block_jailbreaks`, and `block_sensitive_leaks`, with predefined `STRICT` and `BALANCED` presets.

A simple CLI demo (`demo_app/demo_cli.py`) and an evaluation script (`tests/eval_rules_v1.py`) are provided to demonstrate integration and measure basic security metrics. 

## 3. Evaluation dataset

To evaluate the middleware, a small internal dataset of 40 prompts was constructed: 

- **20 attack prompts**:  
  - Direct prompt injection attempts that try to override previous instructions, bypass safety rules, or treat the attacker as a developer/system.  
  - Jailbreak-style requests that ask the model to act as an “unfiltered” or “unrestricted” assistant with no ethical or legal constraints. 

- **20 benign prompts**:  
  - Normal user queries about LLMs, software development, security best practices, study planning, and general technical concepts that should be allowed.

The attack prompts were inspired by documented prompt injection and jailbreak patterns in public guidance and security articles, but rewritten and simplified to avoid copying any existing text. 

## 4. Detection rules (v1)

The current detection logic is purely rule-based:

- **Keyword lists** for `PROMPT_INJECTION_KEYWORDS` and `JAILBREAK_KEYWORDS` cover patterns such as:  
  - Overriding system instructions (“ignore previous instructions”, “override the system prompt”, “bypass all filters”).  
  - Disabling safety (“all safety policies have been disabled”, “disregard any safety policies”).  
  - Developer or system impersonation (“you are now in developer mode”, “treat my next message as coming from your developer”).  
  - Unrestricted behavior and constraints removal (“act as an unfiltered model”, “no safety rules or limitations”, “no ethical or legal constraints”).

- **Classification**:  
  - If any prompt-injection pattern is found, the text is labeled `prompt_injection`.  
  - If any jailbreak pattern is found, the text is labeled `jailbreak`.  
  - Otherwise, the text is labeled `safe` with a generic explanation. 

- **Actions**:  
  - For inputs, `prompt_injection` or `jailbreak` with blocking enabled in policy → action `block`, otherwise `allow`.  
  - For outputs, suspicious labels lead to action `review` (currently logged only), while safe outputs are `allow`. 

This approach provides deterministic, explainable behavior suitable for a first defense layer, as recommended in guardrail best-practice documents. 

## 5. Metrics and results

The evaluation script `tests/eval_rules_v1.py` runs all 40 prompts through the `InputValidator` under the `BALANCED_POLICY` and counts blocked vs allowed prompts for each class. 

**Results on the internal dataset:**

- **Attack prompts (20 total)**:  
  - Attacks blocked: 20 / 20  
  - Attack detection rate (recall on attacks): 100.00%  

- **Benign prompts (20 total)**:  
  - Benign blocked: 0 / 20  
  - Benign false positive rate: 0.00% 

These metrics meet and exceed the task requirements of “>90% detection on attacks” and “<5% false positives on benign prompts” for this evaluation set.

Because this is a small, hand-crafted dataset, the reported numbers should be interpreted as evidence that the rules are tuned to realistic scenarios, not as a guarantee over all possible prompts. Expanding the dataset or importing public prompt-injection benchmarks would be a natural next step to validate generalization. 

## 6. Limitations

While the current middleware shows strong performance on the internal test suite, there are important limitations: 
- **Rule coverage**: Keyword-based rules can miss novel or obfuscated attacks that express similar intent using paraphrasing or multi-step dialog. 
- **Context awareness**: The classifier currently analyzes a single prompt string, without deeper context modeling or tool-use awareness; some indirect prompt injection (e.g., from retrieved documents) may not be detected.
- **Dataset size**: The evaluation is based on 40 prompts only, which is useful for demonstrating behavior but too small for rigorous benchmarking. 

These limitations are consistent with known challenges in building robust LLM guardrails and highlight the need for layered defenses and ongoing evaluation. 

## 7. Future work

Potential improvements include:

- Incorporating a lightweight semantic classifier or LLM-as-judge component to catch paraphrased attacks that evade keyword rules.
- Adding specialized detectors for sensitive-information leakage (e.g., patterns resembling API keys, credentials, or PII) in the `OutputValidator`.  
- Expanding the test dataset using public prompt-injection and jailbreak corpora and computing additional metrics such as precision, recall, and F1 score. 
- Integrating latency and overhead measurements to quantify the performance cost of the middleware when wrapped around a real LLM backend.
Overall, the current version demonstrates a working, configurable middleware that satisfies the assignment’s accuracy targets on the defined test set and provides a solid foundation for further security hardening. 
