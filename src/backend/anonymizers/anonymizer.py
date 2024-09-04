from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine, OperatorConfig
from typing import List, Tuple
from abc import ABC, abstractmethod
from sklearn.metrics import precision_score, recall_score, f1_score
from evaluation import calculate_metrics

class Anonymizer(ABC):
    def __init__(self, *, conf_file: str, 
                 models_file: str,
                 entities: List[str] = ["ORGANIZATION"]) -> None:
        self.conf_file = conf_file
        self.models_file = models_file
        self.entities = entities
        
    def _anonymize(self, texts, results):
        # Initialize the Anonymizer engine
        anonymizer = AnonymizerEngine()

        # Define the anonymization configuration
        # Create an operator configuration for each entity type
        operators = {}
        for entity in self.entities:
            # Create replacement text based on the entity type
            replacement_text = f"[{entity}]"
            anonymization_config = OperatorConfig(operator_name="replace", params={"new_value": replacement_text})
            operators[entity] = anonymization_config
            
        # Anonymize the text
        anonymized_texts = []
        for i, text in enumerate(texts):
            anonymized_text = anonymizer.anonymize(text=text, 
                                                analyzer_results=results[i], 
                                                operators=operators).text
            anonymized_texts.append(anonymized_text)

            print("\t\tOriginal text:", text)
            print("\t\tAnonymized text:", anonymized_text)
            print("\t\t________________________________________________________\n")
            
        return anonymized_texts


    def _analyze(self, texts, nlp_configuration):
        # Create NLP engine based on configuration
        provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
        nlp_engine = provider.create_engine()

        # Pass the created NLP engine and supported_languages to the AnalyzerEngine
        analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine, 
            supported_languages=["en"]
        )

        results = [analyzer.analyze(text=text, entities=self.entities, language="en") for text in texts]
        return results

    def do_anonymize(self, texts, true_annotations=None):
        nlp_configuration_gen = self._get_nlp_configuration()
        for model, nlp_configuration in nlp_configuration_gen:
            # Create NLP engine based on configuration
            provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
            nlp_engine = provider.create_engine()
            
            # Extract the NLP engine details (Assuming the config contains this information)
            nlp_engine_name = nlp_configuration.get('nlp_engine_name', 'Unknown Engine')
            
            # Alternatively, if the config does not contain engine information,
            # you might need to infer this from the provider or engine object directly.
            # For demonstration purposes, we print a placeholder name here.
            print(f"\n\t\t***************************************************")
            print(f"\t\t             Model: {model}                 ")
            print(f"\t\t             NLP Engine: {nlp_engine_name}                 ")
            print(f"\t\t***************************************************")

            # Analyze texts and get results
            results = self._analyze(texts, nlp_configuration)
            
            # Anonymize texts based on results
            anonymized_texts = self._anonymize(texts, results)

            # If true annotations are provided, evaluate the anonymization
            if true_annotations:
                self.evaluate_anonymization(results, true_annotations)
        
        return anonymized_texts


    def evaluate_anonymization(self, results, true_annotations):
        predicted_annotations = self.extract_predicted_annotations(results)
        global_precision, global_recall, global_f1, entity_metrics = calculate_metrics(true_annotations, predicted_annotations)
        
        # Print global metrics
        print("\n\t\t╭─────────────────────────────────────────────────────────────╮")
        print("\t\t│                       Global Metrics                        │")
        print("\t\t├─────────────────────────────────────────────────────────────┤")
        print(f"\t\t│ Precision: {global_precision:.2f}%                         ")
        print(f"\t\t│ Recall: {global_recall:.2f}%                              ")
        print(f"\t\t│ F1 Score: {global_f1:.2f}%                                ")
        print("\t\t╰─────────────────────────────────────────────────────────────╯\n")
            # Print metrics by entity
        print("\t\t╭─────────────────────────────────────────────────────────────╮")
        print("\t\t│                   Metrics by Entity                         │")
        print("\t\t├─────────────────────────────────────────────────────────────┤")
        for entity, metrics in entity_metrics.items():
            print(f"\n\t\t│ Entity: {entity:<30} ")
            print(f"\t\t│ Precision: {metrics['precision']:.2f}%                    ")
            print(f"\t\t│ Recall: {metrics['recall']:.2f}%                         ")
            print(f"\t\t│ F1 Score: {metrics['f1']:.2f}%                           ")
            print("\t\t├──────────────────────────────────────────────────────────────")
        
        print("\t\t╰─────────────────────────────────────────────────────────────╯\n")


    def extract_predicted_annotations(self, results):
        predicted_annotations = []
        for result in results:
            entities = [(ent.entity_type, ent.start, ent.end) for ent in result]
            predicted_annotations.append(entities)
        return predicted_annotations

    @abstractmethod
    def _get_nlp_configuration(self):
        pass
