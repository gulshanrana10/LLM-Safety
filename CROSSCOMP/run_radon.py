import subprocess
import argparse
from datetime import datetime
import os
import shutil
import yaml
import socket  # Import to get the host machine name

def run_radon_commands(folder_path: str, global_folder: str):
    """Run Radon commands and save the output to specified path."""
    # Define the current date and time for the output file name
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    # Define the Radon analysis commands and their descriptions
    radon_folders = {
        "cc": "Cyclomatic Complexity",
        "mi": "Maintainability Index",
        "hal": "Halstead Metrics",
    }

    # Create a folder for this specific run inside the radon_analysis folder
    run_folder = os.path.join(global_folder, f"run_{timestamp}")
    os.makedirs(run_folder, exist_ok=True)

    # Define the Radon commands
    commands = {
        "cc": ["radon", "cc", folder_path],
        "mi": ["radon", "mi", folder_path],
        "hal": ["radon", "hal", folder_path],
    }

    for key, description in radon_folders.items():
        # Create a specific folder for each Radon analysis type inside the run folder
        analysis_folder = os.path.join(run_folder, f"{key}_{description.replace(' ', '_')}")
        os.makedirs(analysis_folder, exist_ok=True)
        output_file = os.path.join(analysis_folder, "output.txt")

        with open(output_file, "w") as f:
            command = commands[key]
            try:
                # Run the command and capture the output
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                
                # Write the command and its output to the file
                f.write(f"Command: {' '.join(command)}\n")
                f.write(result.stdout)
                f.write("\n" + "="*80 + "\n")
            except subprocess.CalledProcessError as e:
                # Write any errors to the file
                f.write(f"Command: {' '.join(command)}\n")
                f.write(f"Error: {e}\n")
                f.write("\n" + "="*80 + "\n")

        print(f"Saved {description} results in folder: {analysis_folder}")

def delete_radon_folders(global_folder: str, yaml_file: str):
    """Delete Radon analysis folders except those listed in the YAML file."""
    def load_folders_to_keep(yaml_file: str):
        """Load the folders to keep from the YAML file."""
        with open(yaml_file, "r") as file:
            data = yaml.safe_load(file)
        return set(data.get("folders_to_keep", []))

    def delete_other_folders(global_folder: str, folders_to_keep: set):
        """Delete folders in the global folder except those specified."""
        for folder_name in os.listdir(global_folder):
            folder_path = os.path.join(global_folder, folder_name)
            if os.path.isdir(folder_path) and folder_name not in folders_to_keep:
                print(f"Deleting folder: {folder_path}")
                shutil.rmtree(folder_path)
            else:
                print(f"Keeping folder: {folder_path}")

    # Load folders to keep from YAML file
    folders_to_keep = load_folders_to_keep(yaml_file)
    
    delete_other_folders(global_folder, folders_to_keep)
    # Delete other folders

def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Run Radon commands on a folder and manage analysis outputs.")
    parser.add_argument("-p", "--path", default="./src/backend", required=True, help="Path to the folder to analyze.")
    parser.add_argument("-o", "--output", default="./CROSSCOMP", help="Path to the Radon analysis global folder.")
    parser.add_argument("-d", "--delete", help="Path to the YAML file listing folders to keep. If provided, deletes other folders.")
    
    # Parse the arguments
    args = parser.parse_args()

    # Get the host machine name
    host_name = socket.gethostname()

    # Path to the host folder and radon_analysis folder inside it
    host_folder = os.path.join(args.output, host_name)
    global_folder = os.path.join(host_folder, "radon_analysis")  # radon_analysis folder inside the host folder

    # Create the radon_analysis folder if it doesn't exist
    os.makedirs(global_folder, exist_ok=True)

    # If deletion is requested, perform it before running new analysis
    if args.delete:
        delete_radon_folders(global_folder, args.delete)

    # Run the Radon commands
    run_radon_commands(args.path, global_folder)

if __name__ == "__main__":
    main()
