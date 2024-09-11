
# 📘 **README**

## ⚙️ **Commands**

---

### **📌 Important Notes:**
- **For consistency and to maintain the correct structure**, always run commands from the **root of the GitHub repository**. This helps ensure paths are correctly resolved, and the workflow stays solid across environments.
- **Use the machine's hostname** in the commands to keep results organized and avoid errors.

---

### 1️⃣ **Run Radon Analysis**

```bash
python CROSSCOMP/run_radon.py -p src/backend
```

**🔍 Description:**  
Runs Radon to analyze the complexity of Python code in the `src/backend` directory. Radon provides insights into code complexity and maintainability.

**⚙️ Options:**
- `-p src/backend`: Specifies the path to the directory with Python code to be analyzed.

---

### 2️⃣ **Execute the Pipeline**

```bash
python CROSSCOMP/crosscomp.py --pipeline CROSSCOMP/crosscomp_pipeline.py --output CROSSCOMP
```

**🔍 Description:**  
Executes the anonymization pipeline as defined in `crosscomp_pipeline.py`, saving results and metrics to the `CROSSCOMP` directory.

**💡 Key Reminders:**
- Ensure you **run this from the root** of the GitHub repo.
- **Replace `<HOSTNAME>`** with the machine’s hostname to avoid errors and keep the results properly organized.

**⚙️ Options:**
- `--pipeline CROSSCOMP/crosscomp_pipeline.py`: Path to the pipeline script.
- `--output CROSSCOMP`: Directory where the results will be saved.

---

### 3️⃣ **Clean Up Results**

```bash
python CROSSCOMP/crosscomp_cleaner.py --config CROSSCOMP/conf/keep_folders.yaml --base_dir CROSSCOMP/<HOSTNAME> --hostname <HOSTNAME>
```

**🔍 Description:**  
This command cleans up results by organizing and removing unnecessary files, based on the configuration in `keep_folders.yaml`. It processes the results in the specified base directory while preserving the folders listed in `keep_folders.yaml`.

**💡 Key Reminders:**
- **Replace `<HOSTNAME>`** with the actual hostname of the machine to properly organize results.
- Always **run this command from the root** of the repository for consistent file handling.

**⚙️ Options:**
- `--config CROSSCOMP/conf/keep_folders.yaml`: Path to the YAML file listing folders to be preserved during cleanup.
- `--base_dir CROSSCOMP/<HOSTNAME>`: Base directory containing results to be cleaned.
- `--hostname <HOSTNAME>`: Hostname used to locate specific result directories.

---

### 4️⃣ **Check Spacy Model Info**

```bash
python -m spacy info en_core_web_lg
```

**🔍 Description:**  
Provides information about the `en_core_web_lg` Spacy model, including version, features, and metadata.

**⚙️ Options:**
- `en_core_web_lg`: Name of the Spacy model for which to retrieve information.

