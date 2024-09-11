from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from typing import List
import yaml

from .anonymizer import Anonymizer

class DefaultAnonymizer(Anonymizer):
	def __init__(self, *, conf_file: str, 
              		models_file: str,
                	entities: List[str] = ["ORGANIZATION"]) -> None:
		super().__init__(conf_file=conf_file, models_file=models_file, entities=entities)
	
	def _get_nlp_configuration(self):
		pass

	def do_anonymize(self, texts):
		analyzer = AnalyzerEngine()
		
		if isinstance(texts, list):
			results = []
			for text in texts:
				results.append(analyzer.analyze(text=text, entities=self.entities, language="en"))
		else:
			results = analyzer.analyze(text=texts, entities=self.entities, language="en")
		
		print(f"\n***************************************************")
		print(f"                 Default List                      ")
		print(f"***************************************************")
		anonymized_texts = self._anonymize(texts, results)

		return anonymized_texts