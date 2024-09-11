from typing import List, Dict, Any
import yaml
import spacy

from .anonymizer import Anonymizer

class SpacyAnonymizer(Anonymizer):
    def __init__(self, *, conf_file: str) -> None:
        super().__init__(conf_file=conf_file)
        self.nlp = None  # Placeholder for loading Spacy models
        self.entities = []  # Entities to anonymize will be populated from config

    def _get_nlp_configuration(self) -> Dict[str, Any]:
        """Load the NLP configurations from the provided file."""
        try:
            with open(self.conf_file, "r") as f:
                nlp_configuration = yaml.safe_load(f)
            return nlp_configuration
        except Exception as e:
            raise RuntimeError(f"Failed to load NLP configuration: {e}")
    def extract_and_anonymize(self, ground_truth_path: str) -> List[Dict[str, Any]]:
        """Extract texts from ground truth file and apply anonymization.""" 
        with open(ground_truth_path, 'r') as f:
            data = yaml.safe_load(f)
        
        texts_data = data.get('texts', [])
        
        if not all(isinstance(text, dict) and 'text' in text for text in texts_data):
            raise ValueError("Each entry in texts should be a dictionary with 'text' key.")
        
        texts = [text['text'] for text in texts_data]
        ids = [text.get('id', 'Unknown') for text in texts_data]
        annotations = [text.get('annotations', []) for text in texts_data]
        
        # Apply anonymization
        anonymized_results = self.do_anonymize(texts)
        
        # Attach IDs, annotations, and annotated text to results
        id_to_annotations = {text['text']: text.get('annotations', []) for text in texts_data}
        id_to_text = {text['text']: text['id'] for text in texts_data}
        
        for result in anonymized_results:
            original_text = result['original_text']
            result['id'] = id_to_text.get(original_text, 'Unknown')
            result['annotations'] = id_to_annotations.get(original_text, [])
            result['ground_truth_annotated_text'] = self._generate_annotated_text(original_text, result['annotations'])

        return anonymized_results

    def _generate_annotated_text(self, text: str, annotations: List[Dict[str, Any]]) -> str:
        """Generate annotated text with ground truth annotations."""
        annotated_text = text
        for annotation in sorted(annotations, key=lambda x: x['start'], reverse=True):
            annotated_text = (
                annotated_text[:annotation['start']] 
                + f"<{annotation['label']}>" 
                + annotated_text[annotation['end']:]
            )
        return annotated_text

    def _extract_entities(self, nlp_configuration: Dict[str, Any]) -> List[str]:
        """Extract entities from the configuration file."""
        mapping = nlp_configuration.get("ner_model_configuration", {}).get("model_to_presidio_entity_mapping", {})
        entities = list(mapping.values())  # Get the mapped Presidio entities
        print(f"Extracted entities for anonymization: {entities}")  # Debug print for extracted entities
        return entities

    def _analyze(self, texts: List[str], nlp_configuration: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze and anonymize the texts based on NLP configurations."""
        if self.nlp is None:
            model_config = nlp_configuration.get("models", [{}])[0]
            model_name = model_config.get("model_name", "en_core_web_sm")
            print(f"Loading SpaCy model: {model_name}")  # Debug print for model name
            try:
                self.nlp = spacy.load(model_name)
            except Exception as e:
                raise RuntimeError(f"Failed to load SpaCy model '{model_name}': {e}")

        if not self.entities:
            self.entities = self._extract_entities(nlp_configuration)

        analysis_results = []
        for text in texts:
            doc = self.nlp(text)
            print("Processing text:", text)
            print("Entities found:")

            # Collect entities to anonymize
            labels = []
            for ent in doc.ents:
                if ent.label_ in self.entities:
                    labels.append({
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char
                    })
                    print(f"Entity: {ent.text}, Label: {ent.label_}, Start: {ent.start_char}, End: {ent.end_char}")

            # Anonymize the text by replacing entities in reverse order
            anonymized_text = text
            for label in sorted(labels, key=lambda x: x['start'], reverse=True):
                anonymized_text = (
                    anonymized_text[:label['start']] 
                    + f"<{label['label']}>" 
                    + anonymized_text[label['end']:]
                )
            
            # Add the anonymized result to the output
            analysis_results.append({
                'text': text,
                'anonymized_text': anonymized_text,
                'labels': labels,
                'model_name': model_name
            })

            print("Anonymized text:", anonymized_text)

        return analysis_results

    def do_anonymize(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Apply anonymization to a list of texts.""" 
        nlp_configuration = self._get_nlp_configuration()
        results = self._analyze(texts, nlp_configuration)

        anonymized_texts = []
        for result in results:
            anonymized_texts.append({
                'nlp_engine_name': nlp_configuration.get('nlp_engine_name', 'Spacy NLP Engine'),
                'model': result['model_name'],
                'original_text': result['text'],
                'anonymized_text': result['anonymized_text'],
                'labels': result['labels']
            })

        return anonymized_texts


