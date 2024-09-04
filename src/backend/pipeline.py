from .anonymizers.transformer_anonymizer import TransformerAnonymizer
from .anonymizers.default_anonymizer import DefaultAnonymizer
from .anonymizers.recognizer_anonymizer import RecognizerAnonymizer

def _get_pipeline():
    pipeline = [
		{
			"conf": None,
			"models": None,
			"entities": ["ORGANIZATION", "PERSON", "IP_ADDRESS", "EMAIL_ADDRESS"],
			"provider": DefaultAnonymizer
		},
  		{
			"conf": "PII_masking/conf/conf_transformer.yaml",
			"models": None,
			"entities": ["ORGANIZATION", "PERSON"],
			"provider": TransformerAnonymizer
		},
		{
			"conf": "PII_masking/conf/recognizer_sparse.yaml",
			"models": None,
			"entities": ["ORGANIZATION"],
			"provider": RecognizerAnonymizer
		}
	]
    
    return pipeline

def execute_pipeline(text):
    pipeline = _get_pipeline()
    
    for i, step in enumerate(pipeline):
        provider = step["provider"]
        anonymizer = provider(conf_file=step["conf"], 
                        	  models_file=step["models"],
                           	  entities=step["entities"])
        print(f"STEP {i+1}:")
        text = anonymizer.do_anonymize(text)
    return text
        
if __name__ == "__main__":
	texts = ["I use Verizon for my phone services",
          	"My friend uses AT&T, the best CSP",
           	"In TELUS, AUSF_UDM uses external HSM"]

	for text in texts:
		result = execute_pipeline(text)
		print(f"FINAL TEXT: {result}\n")