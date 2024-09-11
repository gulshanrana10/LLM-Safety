import argparse

from anonymizers.transformer_anonymizer import TransformerAnonymizer
from anonymizers.spacy_anonymizer import SpacyAnonymizer
from anonymizers.recognizer_anonymizer import RecognizerAnonymizer
from anonymizers.default_anonymizer import DefaultAnonymizer

def _get_text():
    parser = argparse.ArgumentParser(description="Anonymize PII in the provided text")
    parser.add_argument('-t', '--text', 
                        type=str, 
                        required=False, 
                        help='text from which the PII needs to be anonymized')
    args = parser.parse_args()
    if args.text:
        return args.text
    else:
        texts = ["I use Verizon for my phone services",
                 "My friend uses AT&T, the best CSP",
                 "In TELUS, AUSF_UDM uses external HSM"]
        return texts

if __name__ == "__main__":
    texts = _get_text()
    configs = [
		{
			"conf": "src/backend/conf/conf_transformer.yaml",
			"models": "src/backend/conf/models_ner.yaml",
			"entities": ["ORGANIZATION", "PERSON"],
			"provider": TransformerAnonymizer
		},
		{
			"conf": "src/backend/conf/conf_spacy.yaml",
			"models": "src/backend/conf/models_spacy.yaml",
			"entities": ["ORGANIZATION", "PERSON"],
			"provider": SpacyAnonymizer
		},
		{
			"conf": "src/backend/conf/recognizer.yaml",
			"models": None,
			"entities": ["ORGANIZATION"],
			"provider": RecognizerAnonymizer
		},
		{
			"conf": None,
			"models": None,
			"entities": ["ORGANIZATION", "PERSON", "IP_ADDRESS", "EMAIL_ADDRESS"],
			"provider": DefaultAnonymizer
		}
	]
    
    for config in configs:
        provider = config["provider"]
        anonymizer = provider(conf_file=config["conf"], 
                        	  models_file=config["models"], 
                           	  entities=config["entities"])
        anonymizer.do_anonymize(texts)