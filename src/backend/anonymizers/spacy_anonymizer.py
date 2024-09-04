from typing import List
import yaml

from .anonymizer import Anonymizer

class SpacyAnonymizer(Anonymizer):
	def __init__(self, *, conf_file: str, 
              		models_file: str,
                	entities: List[str] = ["ORGANIZATION"]) -> None:
		super().__init__(conf_file=conf_file, models_file=models_file, entities=entities)
	
	def _get_nlp_configuration(self):
		with open(self.conf_file, "r") as f:
			nlp_configuration = yaml.safe_load(f)
		
		if self.models_file is not None:
			with open(self.models_file, "r") as f:
				models = yaml.safe_load(f)["models"]
				
			for model in models:
				nlp_configuration["models"][0]["model_name"] = model
				yield (model, nlp_configuration)
		else:
			model = nlp_configuration["models"][0]["model_name"]
			yield model, nlp_configuration
