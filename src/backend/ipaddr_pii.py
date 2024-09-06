from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
import re


class SecretRecognizer(PatternRecognizer):
    def __init__(self):
        patterns = [Pattern("secret pattern", r"secret", 0.85)]
        super().__init__(supported_entity="MY_CUSTOM_ENTITY", patterns=patterns)


class IPAddressRecognizer(PatternRecognizer):
    def __init__(self):
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        patterns = [Pattern("IP address pattern", ip_pattern, 0.9)]
        super().__init__(supported_entity="IP_ADDRESS", patterns=patterns)


analyzer = AnalyzerEngine()


secret_recognizer = SecretRecognizer()
ip_recognizer = IPAddressRecognizer()
analyzer.registry.add_recognizer(secret_recognizer)
analyzer.registry.add_recognizer(ip_recognizer)


text = "This is a secret document. The server IP is 192.168.1.1."
results = analyzer.analyze(text=text, entities=["MY_CUSTOM_ENTITY", "IP_ADDRESS"], language="en")


for result in results:
    print(f"Detected entity: {result.entity_type}, Text: {text[result.start:result.end]}, Confidence Score: {result.score}")
