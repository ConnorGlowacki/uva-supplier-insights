# 🧠 SupplyPy

**SupplyPy** is a command-line tool for extracting insights from UVA supplier transaction data. Designed for specifically structured CSV-based input, it provides utilities for preprocessing, analyzing, and preparing data related to purchase orders, delivery schedules, and supplier performance.

---

## 📦 Features

- 🔍 Clean and process raw supplier CSVs
- 📊 Analyze supplier transactions
- ⚙️ CLI-driven workflow with extensibility in mind
- ✅ Built with Python 3.11 and `setuptools` using a modern `pyproject.toml` layout

---

## 🛠️ Installation

```bash
git clone https://github.com/YOUR_USERNAME/supplypy.git
cd supplypy
conda create -n supplypy-dev python=3.11
conda activate supplypy-dev

pip install .
```

If you are a developer, install the package using: 

```bash
pip install -e .
```

This allows live reloading of code changes.

## Setup

### Conda

One of the easiest ways to manage data science projects is through `conda`. If you don't already have Conda installed, download and install [Miniconda or Anaconda](https://docs.conda.io/projects/conda/en/stable/user-guide/install/windows.html)

### HuggingFace

You will need to have a [HuggingFace](https://huggingface.co/) account in order to download the `sentence_transformers` model used to create semantic embeddings. See instructions from HuggingFace [here](https://huggingface.co/docs/timm/en/hf_hub).

### TabPy

Additionally, if you are connecting to a _TabPy_ server that uses authentication, you will have provide authentication details to the client creation step in the `deploy_services` function. There are instructions on how to do so in TabPy's [documentation](https://tableau.github.io/TabPy/docs/tabpy-tools.html#authentication), but the cli should provide arguments to pass this information.

## 🚀 Usage

### Building

```bash
supplypy build
```

This command is intended to be run prior to deploying any modeling services. This kicks off the process of ingesting the provided data and building the models that will be used for inference during run time.

> Note: This took about 20 minutes on my local machine running a Nvidia RTX 2070 --Connor

### Running TabPy

If `tabpy` is installed, you can run an unauthenticated server by simply running:

```bash
tabpy
```

Ensure that the `tabpy` process is run from the project directory or has access to the files in this repo. You should see an output like this:

```text
(supplypy-dev) B:\OneDrive\Documents\code\school\uva-supplier-insights>tabpy
2025-04-28,22:37:27 [INFO] (app.py:app:316): Parsing config file D:\miniforge3\envs\supplypy-dev\Lib\site-packages\tabpy\tabpy_server\app\..\common\default.conf
2025-04-28,22:37:27 [INFO] (app.py:app:381): Setting max request size to 104857600 bytes
2025-04-28,22:37:27 [INFO] (app.py:app:545): Loading state from state file D:\miniforge3\envs\supplypy-dev\Lib\site-packages\tabpy\tabpy_server\state.ini

WARNING: This TabPy server is not currently configured for username/password authentication. This means that, because the TABPY_EVALUATE_ENABLE feature is enabled, there is the potential that unauthenticated individuals may be able to remotely execute code on this machine. We strongly advise against proceeding without authentication as it poses a significant security risk.

Do you wish to proceed without authentication? (y/N): y
2025-04-28,22:37:30 [INFO] (app.py:app:510): Password file is not specified: Authentication is not enabled
2025-04-28,22:37:30 [INFO] (app.py:app:429): Call context logging is disabled
2025-04-28,22:37:30 [INFO] (app.py:app:197): Initializing TabPy...
2025-04-28,22:37:30 [INFO] (callbacks.py:callbacks:43): Initializing TabPy Server...
2025-04-28,22:37:30 [INFO] (app.py:app:201): Done initializing TabPy.
```

### Deploying

> A TabPy server instance must be running and `build` must have been run prior to this command

```bash
supplypy deploy
```

This command will create HTTP endpoints in the TabPy server that can be used in Tableau applications. You _must_ ensure that the TabPy server in running in this directory or has access to these files so that IO operations do not fail.

Output will look like this:

```text
Dispatching command...
Deploying TabPy Services...
```

#### Command Line Options:

- `--host` to specify a TabPy server URL to deploy tools to
- `--username` and `--password` to specify authentication details if needed


## 🗂️ Project Structure

```graphql
supplypy/
├── cli.py                     # CLI entrypoint
├── service/
│   ├── __init__.py
│   └── preprocessing.py       # Main CSV processing logic
data/
├──TRANSACTIONS.csv
├── transactions/
│   ├── ...
outputs/
├── ...
```
> Note that these directories do not exist when the repo is initially cloned. The only directory the user is expected to create is `data/transactions`, as this is well multiple transaction exports can be placed in order to provide the models data

## A note to developers

Future enhancements should include environment configurability, because everything is currently hard coded.