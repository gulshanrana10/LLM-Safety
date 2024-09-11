import yaml
import sys
import os
import importlib
import time
from typing import List, Dict, Any
from evaluation_helper import evaluate_results

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/backend')))
from anonymizers.spacy_anonymizer import SpacyAnonymizer  # Explicit import of SpacyAnonymizer

def load_pipeline_from_yaml(file_path):
    """Load pipeline configuration from a YAML file."""
    with open(file_path, 'r') as f:
        config = yaml.safe_load(f)
    return config['pipeline']

def get_provider_class(provider_name):
    """Dynamically import and return the provider class."""
    try:
        module_mapping = {
            'SpacyAnonymizer': 'spacy_anonymizer',
        }
        module_name = module_mapping.get(provider_name, provider_name.lower())
        module = importlib.import_module(f'anonymizers.{module_name}')
        provider_class = getattr(module, provider_name)
        return provider_class
    except ModuleNotFoundError:
        raise ImportError(f"Module for provider {provider_name} not found.")
    except AttributeError:
        raise ImportError(f"Provider class {provider_name} not found in module {module_name}.")

def save_evaluation_metrics(metrics, output_dir, pipeline_step, execution_time=None):
    """Save evaluation metrics and optionally execution time to a file."""
    metrics_file = os.path.join(output_dir, f'pipeline_{pipeline_step}_evaluation_metrics.txt')
    with open(metrics_file, 'w') as file:
        file.write(f"Global Evaluation Metrics:\n")
        file.write(f"Precision: {metrics['global']['precision']:.4f}\n")
        file.write(f"Recall: {metrics['global']['recall']:.4f}\n")
        file.write(f"F1 Score: {metrics['global']['f1_score']:.4f}\n")
        file.write("\nEntity-Specific Evaluation Metrics:\n")
        for entity, metrics in metrics['by_entity'].items():
            file.write(f"Entity: {entity}\n")
            file.write(f"  Precision: {metrics['precision']:.4f}\n")
            file.write(f"  Recall: {metrics['recall']:.4f}\n")
            file.write(f"  F1 Score: {metrics['f1_score']:.4f}\n")
        
        if execution_time is not None:
            file.write("\nExecution Time:\n")
            file.write(f"Step Execution Time: {execution_time:.2f} seconds\n")

def execute_pipeline(config_file_path, output_dir):
    """Execute the pipeline steps as defined in the configuration file."""
    pipeline = load_pipeline_from_yaml(config_file_path)
    print("\n\nPIPELINES EXECUTION LAUNCH\n")
    all_results = []

    os.makedirs(output_dir, exist_ok=True)

    if pipeline:
        for i, step in enumerate(pipeline):
            start_time = time.time()  # Start timing
            provider_class_name = step["provider"]
            try:
                provider_class = get_provider_class(provider_class_name)
                print(f"Provider class found: {provider_class_name} -> {provider_class}")
            except ImportError as e:
                print(e)
                continue

            conf_file = step.get("conf")
            anonymizer = provider_class(conf_file=conf_file)
            
            if isinstance(anonymizer, SpacyAnonymizer):
                ground_truth_path = step.get("ground_truth_path")
                results = anonymizer.extract_and_anonymize(ground_truth_path)
            else:
                raise TypeError("Unsupported anonymizer type.")
            end_time = time.time()  # End timing
            step_duration = end_time - start_time
            print(f"Step {i+1} took {step_duration:.2f} seconds")

            print(f"PIPELINE :{i+1}:")
            for result in results:
                print(f"ID: {result.get('id', 'Unknown')}")
                print(f"Original text: {result['original_text']}")
                print(f"Anonymized text: {result['anonymized_text']}")
                print(f"Ground Truth Annotated Text: {result.get('ground_truth_annotated_text', 'N/A')}")
                print(f"NLP Engine: {result['nlp_engine_name']}")
                print(f"Model: {result['model']}")
                print(f"Anonymization Details: {result.get('annotations', 'No annotation details found')}")
                print("\n" + "\n")
            
            print("Debug Info for Results and Extracted Data:")
            for result in results:
                print("Result ID:", result.get('id', 'Unknown'))
                print("Anonymized Text:", result['anonymized_text'])
                print("Ground Truth Annotated Text:", result.get('ground_truth_annotated_text', 'N/A'))
                print("Extracted Labels:", result.get('annotations', 'No annotation details found'))
                print("="*40)
            
            all_results.append((i+1, results, step_duration))
    
    ground_truth_path = pipeline[0].get("ground_truth_path", None)
    if ground_truth_path:
        for step, results, step_duration in all_results:
            evaluation_metrics = evaluate_results(results, ground_truth_path)
            save_evaluation_metrics(evaluation_metrics, output_dir, step, execution_time=step_duration)
    
    return all_results

if __name__ == "__main__":
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'crosscomp_results'
    results = execute_pipeline('CROSSCOMP/conf/pipeline_config.yaml', output_dir)
    print("EXITING crosscomp_pipeline.py\n")
