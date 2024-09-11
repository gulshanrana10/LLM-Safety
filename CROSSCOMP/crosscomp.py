import sys
import argparse
import subprocess
import os
import socket
from datetime import datetime

def save_results_to_file(results, output_dir, pipeline_step, metrics=None):
    """Save the results and metrics to files for each pipeline step."""
    results_file = os.path.join(output_dir, f'pipeline_{pipeline_step}_results.txt')
    metrics_file = os.path.join(output_dir, f'pipeline_{pipeline_step}_metrics.txt')

    with open(results_file, 'w') as file:
        for entry in results:
            file.write(f"NLP Engine: {entry.get('nlp_engine_name', 'N/A')}\n")
            file.write(f"Model: {entry.get('model', 'N/A')}\n")
            file.write(f"Original Text: {entry.get('original_text', 'N/A')}\n")
            file.write(f"Ground Truth Annotated Text: {entry.get('ground_truth_annotated_text', 'N/A')}\n")  # Updated line
            file.write(f"Anonymized Text: {entry.get('anonymized_text', 'N/A')}\n")
            file.write(f"Anonymization Details: {entry.get('annotations', 'N/A')}\n")
            file.write("\n" + "="*40 + "\n\n")

    if metrics:
        with open(metrics_file, 'w') as file:
            file.write(f"Precision: {metrics['precision']:.4f}\n")
            file.write(f"Recall: {metrics['recall']:.4f}\n")
            file.write(f"F1 Score: {metrics['f1_score']:.4f}\n")


            
def parse_pipeline_output(output):
    """Parse the pipeline's stdout output and extract anonymization results."""
    results = []
    entry = {}
    pipeline_step = 0

    lines = output.strip().split('\n')

    for line in lines:
        if line.startswith("PIPELINE :"):
            pipeline_step = int(line.split(":")[1].strip())
        elif line.startswith("Original text: "):
            entry['original_text'] = line[len("Original text: "):].strip()
        elif line.startswith("Anonymized text: "):
            entry['anonymized_text'] = line[len("Anonymized text: "):].strip()
        elif line.startswith("Ground Truth Annotated Text: "):
            entry['ground_truth_annotated_text'] = line[len("Ground Truth Annotated Text:"):].strip()
        elif line.startswith("NLP Engine: "):
            entry['nlp_engine_name'] = line[len("NLP Engine: "):].strip()
        elif line.startswith("Model: "):
            entry['model'] = line[len("Model: "):].strip()
        elif line.startswith("Anonymization Details:"):
            entry['annotations'] = line[len("Anonymization Details:"):].strip()
        elif line.strip() == '' and entry:  # End of an entry
            if 'original_text' in entry and 'anonymized_text' in entry:
                results.append((pipeline_step, entry))
            entry = {}  # Reset for the next entry

    return results



def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run pipeline and track original/anonymized texts.")
    parser.add_argument('-p', '--pipeline', type=str, required=True,
                        help='Path to the pipeline Python file (e.g., pipeline.py).')
    parser.add_argument('-o', '--output', type=str, default='crosscomp',
                        help='Path to the output directory where results will be saved.')
    parser.add_argument('--config', type=str, default='CROSSCOMP/conf/keep_folders.yaml',
                        help='Path to the configuration YAML file (default: CROSSCOMP/conf/keep_folders.yaml).')

    args = parser.parse_args()

    # Get the host machine name
    host_name = socket.gethostname()

    # Generate a timestamp for the main folder and file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Define the hostname folder and results folder
    hostname_folder = os.path.join(args.output, host_name)
    os.makedirs(hostname_folder, exist_ok=True)

    # Define the crosscomp_results folder inside the hostname folder
    results_folder = os.path.join(hostname_folder, 'crosscomp_results')
    os.makedirs(results_folder, exist_ok=True)

    # Create a timestamped folder inside crosscomp_results
    timestamped_folder = os.path.join(results_folder, f'run_{timestamp}')
    os.makedirs(timestamped_folder, exist_ok=True)

    # Call the pipeline.py script using subprocess and pass the output directory
    command = [
        'python', args.pipeline,
        '--output', timestamped_folder  # Pass the output directory argument
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Capture and print real-time output
    stdout_lines = []
    for line in iter(process.stdout.readline, ''):
        sys.stdout.write(line)  # Print to terminal
        sys.stdout.flush()
        stdout_lines.append(line)  # Store the output line for later parsing

    stdout, stderr = process.communicate()  # Wait for process to complete
    stdout_lines.append(stdout)  # Append remaining output (if any)

    if process.returncode == 0:
        # Parse the pipeline output and handle results
        full_output = ''.join(stdout_lines)  # Combine the captured output
        parsed_results = parse_pipeline_output(full_output)
        
        # Separate and save results per pipeline step
        pipeline_results = {}
        for step, result in parsed_results:
            if step not in pipeline_results:
                pipeline_results[step] = []
            pipeline_results[step].append(result)
        
        # Save each pipeline's results in a separate file
        for step, results in pipeline_results.items():
            save_results_to_file(results, timestamped_folder, step)
        
        print(f"Results saved to {timestamped_folder}\n")
        
    else:
        print(f"Error in pipeline execution: {stderr}")
    print("CROSS COMP PROG DONE AND EXIT")

if __name__ == "__main__":
    main()
