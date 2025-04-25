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

# Editable install
pip install -e .
```

## 🚀 Usage

Example commands:

```bash
supplypy build
supplypy deploy
```

## 🗂️ Project Structure

```graphql
supplypy/
├── cli.py                     # CLI entrypoint
├── service/
│   ├── __init__.py
│   └── preprocessing.py       # Main CSV processing logic

```