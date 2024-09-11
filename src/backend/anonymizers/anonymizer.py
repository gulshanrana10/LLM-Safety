from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine, OperatorConfig
from typing import List, Dict, Any
from abc import ABC, abstractmethod
import yaml

class Anonymizer(ABC):
    def __init__(self, *, conf_file: str, 
                 models_file: str = None,  # Make models_file optional
                 entities: List[str] = ["ORGANIZATION"]) -> None:
        self.conf_file = conf_file
        self.models_file = models_file
        self.entities = entities
    
    def _anonymize(self, texts: List[str], results: List[List[Dict[str, Any]]]) -> List[str]:
        """Anonymize the texts based on provided results."""
        anonymizer = AnonymizerEngine()
        anonymization_config = OperatorConfig(operator_name="replace", params={"new_value": "****"})
        operators = {entity: anonymization_config for entity in self.entities}
        
        if isinstance(texts, list):
            anonymized_texts = []
            for i in range(len(texts)):
                anonymized_texts.append(anonymizer.anonymize(
                    text=texts[i], 
                    analyzer_results=results[i], 
                    operators=operators
                ).text)
        else:
            anonymized_texts = anonymizer.anonymize(
                text=texts, 
                analyzer_results=results, 
                operators=operators
            ).text
        
        return anonymized_texts

    def _analyze(self, texts: List[str], nlp_configuration: Dict[str, Any]) -> List[List[Dict[str, Any]]]:
        """Analyze texts using the provided NLP configuration."""
        provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
        nlp_engine = provider.create_engine()

        analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine, 
            supported_languages=["en"]
        )

        if isinstance(texts, list):
            results = []
            for text in texts:
                results.append(analyzer.analyze(text=text, entities=self.entities, language="en"))
        else:
            results = analyzer.analyze(text=texts, entities=self.entities, language="en")
        
        return results

    def do_anonymize(self, texts: List[str]) -> List[str]:
        """Apply anonymization to the texts."""
        nlp_configurations = self._get_nlp_configuration()
        anonymized_texts = []

        for model, nlp_configuration in nlp_configurations:
            results = self._analyze(texts, nlp_configuration)
            anonymized_texts.extend(self._anonymize(texts, results))
        
        return anonymized_texts

    @abstractmethod
    def _get_nlp_configuration(self) -> List[Dict[str, Any]]:
        """Return the NLP configurations required for the analyzer."""
        pass
