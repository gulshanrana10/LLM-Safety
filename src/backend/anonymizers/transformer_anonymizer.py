import yaml
from typing import List
from .anonymizer import Anonymizer

class TransformerAnonymizer(Anonymizer):
    def __init__(self, *, conf_file: str, 
                 models_file: str,
                 entities: List[str] = ["ORGANIZATION"]) -> None:
        super().__init__(conf_file=conf_file, models_file=models_file, entities=entities)

    def _get_nlp_configuration(self):
        with open(self.conf_file, "r") as f:
            nlp_configuration = yaml.safe_load(f)
        
        if self.models_file:
            with open(self.models_file, "r") as f:
                models = yaml.safe_load(f)["models"]
                
            for model in models:
                # Update the configuration with the current model
                nlp_configuration["models"][0]["model_name"]["transformers"] = model
                yield (model, nlp_configuration)
        else:
            model = nlp_configuration["models"][0]["model_name"]["transformers"]
            yield (model, nlp_configuration)
