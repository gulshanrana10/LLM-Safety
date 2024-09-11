import yaml
import os
import shutil

def load_keep_folders(file_path):
    """Load the YAML configuration for keeping folders."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def delete_unwanted_folders(base_dir, keep_folders_config, hostname):
    """Delete folders in base_dir that are not listed in keep_folders_config."""
    if hostname not in keep_folders_config:
        print(f"No folders specified to keep for hostname {hostname}")
        return

    categories_to_keep = keep_folders_config[hostname]

    # Define directories to clean
    directories_to_clean = [
        os.path.join(base_dir, 'crosscomp_results'),
        os.path.join(base_dir, 'radon_analysis')
    ]

    for dir_type in directories_to_clean:
        dir_name = os.path.basename(dir_type)
        if dir_name in categories_to_keep:
            keep_folders = categories_to_keep[dir_name]
            if os.path.exists(dir_type):
                for folder_name in os.listdir(dir_type):
                    folder_path = os.path.join(dir_type, folder_name)
                    if os.path.isdir(folder_path):
                        if folder_name not in keep_folders:
                            shutil.rmtree(folder_path)
                            print(f"Deleted folder {folder_path}")
                        else:
                            print(f"Keeping folder {folder_path}")
            else:
                print(f"Directory {dir_type} does not exist.")
        else:
            print(f"No category found for {dir_name} in the keep configuration.")

if __name__ == "__main__":
    import argparse

    # Setup command-line argument parsing
    parser = argparse.ArgumentParser(description="Manage folders based on keep configuration.")
    parser.add_argument('--config', type=str, required=True, help="Path to the YAML configuration file.")
    parser.add_argument('--base_dir', type=str, required=True, help="Base directory for cleaning.")
    parser.add_argument('--hostname', type=str, required=True, help="Hostname for folder management.")

    args = parser.parse_args()

    # Load the YAML configuration
    keep_folders_config = load_keep_folders(args.config)

    # Delete unwanted folders
    delete_unwanted_folders(args.base_dir, keep_folders_config, args.hostname)
