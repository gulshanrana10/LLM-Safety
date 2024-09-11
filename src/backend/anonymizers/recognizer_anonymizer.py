from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from typing import List
import yaml

from .anonymizer import Anonymizer

class RecognizerAnonymizer(Anonymizer):
	def __init__(self, *, conf_file: str, 
              		models_file: str,
                	entities: List[str] = ["ORGANIZATION"]) -> None:
		super().__init__(conf_file=conf_file, models_file=models_file, entities=entities)
	
	def _get_nlp_configuration(self):
		registry = RecognizerRegistry()
		registry.load_predefined_recognizers()

		registry.add_recognizers_from_yaml(self.conf_file)
		return registry

	def do_anonymize(self, texts):
		registry = self._get_nlp_configuration()
		analyzer = AnalyzerEngine(registry=registry)
  
		if isinstance(texts, list):
			results = []
			for text in texts:
				results.append(analyzer.analyze(text=text, entities=self.entities, language="en"))
		else:
			results = analyzer.analyze(text=texts, entities=self.entities, language="en")
		
		print(f"\n***************************************************")
		print(f"                 Custom List                      ")
		print(f"***************************************************")
		anonymized_texts = self._anonymize(texts, results)

		return anonymized_texts