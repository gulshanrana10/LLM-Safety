import yaml
from anonymizers.transformer_anonymizer import TransformerAnonymizer
from anonymizers.spacy_anonymizer import SpacyAnonymizer
from anonymizers.recognizer_anonymizer import RecognizerAnonymizer
from anonymizers.default_anonymizer import DefaultAnonymizer
import yaml

def _get_text_from_ground_truth(ground_truth):
    with open(ground_truth, 'r') as file:
        data = yaml.safe_load(file)
        # Extract text strings and annotations
        texts = [item['text'] for item in data['texts']]
        annotations = [item['annotations'] for item in data['texts']]
        return texts, annotations
def print_config_details(config):
    """
    Print details of the anonymization configuration.
    
    """
    print("\t\t#################################################################")
    print(f"\n╭─────────────────────────────────────────────────────────────╮")
    print(f"│       Anonymization Configuration                           │")
    print(f"├─────────────────────────────────────────────────────────────┤")
    print(f"│ Configuration File: {config['conf'] if config['conf'] else 'None':<30} ")
    print(f"│ Models File: {config['models'] if config['models'] else 'None':<30} ")
    print(f"│ Entities to Anonymize: {', '.join(config['entities']):<30} ")
    print(f"│ Provider: {config['provider'].__name__: <30} ")
    print(f"│ Ground Truth File: {config['ground_truth'] if config['ground_truth'] else 'None':<30}")
    print(f"╰─────────────────────────────────────────────────────────────╯\n")
    

if __name__ == "__main__":
    configs = [
        {
            "conf": "src\\backend\\conf\\conf_transformer.yaml",
            "models": "src\\backend\\conf\\models_ner.yaml",
            "entities": ["ORGANIZATION", "PERSON"],
            "provider": TransformerAnonymizer,
            "ground_truth": "src\\backend\\conf\\ground_truth.yaml"
        },
        {
            "conf": "src\\backend\\conf\\conf_spacy.yaml",
            "models": "src\\backend\\conf\\models_spacy.yaml",
            "entities": ["ORGANIZATION", "PERSON"],
            "provider": SpacyAnonymizer,
            "ground_truth": "src\\backend\\conf\\ground_truth.yaml"
        },
        {
            "conf": "src\\backend\\conf\\recognizer.yaml",
            "models": None,
            "entities": ["ORGANIZATION"],
            "provider": RecognizerAnonymizer,
            "ground_truth": "src\\backend\\conf\\ground_truth.yaml"
        },
        {
            "conf": None,
            "models": None,
            "entities": ["ORGANIZATION", "PERSON"],
            "provider": DefaultAnonymizer,
            "ground_truth": "src\\backend\\conf\\ground_truth.yaml"
        }
    ]
    
    for config in configs:
        print_config_details(config)
        texts, true_annotations = _get_text_from_ground_truth(config["ground_truth"])
        provider = config["provider"]
        anonymizer = provider(conf_file=config["conf"], 
                              models_file=config["models"], 
                              entities=config["entities"])
        anonymizer.do_anonymize(texts, true_annotations=true_annotations)
