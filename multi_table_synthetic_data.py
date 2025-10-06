"""
multi_table_synthetic_data.py
my_project/
├── data/
│   └── customer/
├── modules/
│   ├── config.py
│   ├── data_loader.py
│   ├── metadata_loader.py
│   ├── synthesizer.py
│   ├── writer.py
│   ├── evaluator.py
│   └── timer.py
└── main.py


Generate synthetic customer, email, phone, and address tables using
SDV's HMASynthesizer, preserving referential integrity,
and write them out as CSVs for testing.

This script is modular and reusable. Configuration, data loading,
synthetic data generation, output writing, and evaluation are separated
into distinct functions. All functions are documented for clarity.
"""

import os
import time
import logging
import pandas as pd
from typing import Dict, Tuple
from sdv.metadata.multi_table import MultiTableMetadata
from sdv.multi_table import HMASynthesizer
from sdv.evaluation.multi_table import evaluate_quality

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
NUM_CUSTOMERS = 10
CSV_DIR = '/Users/rahulchakraborty/Documents/Study/Data_Engineering/my_project/data/customer'

INPUT_EMAIL = 'customer_email_details.csv'
INPUT_PHONE = 'customer_phone_details.csv'
INPUT_ADDRESS = 'customer_address_details.csv'

OUT_CUSTOMER = 'synthetic_customer.csv'
OUT_EMAIL = 'synthetic_customer_email.csv'
OUT_PHONE = 'synthetic_customer_phone.csv'
OUT_ADDRESS = 'synthetic_customer_address.csv'
OUT_TIME_LOG = 'execution_time.txt'
METADATA_JSON = 'my_metadata_v1.json'

# -----------------------------------------------------------------------------
# DATA LOADING
# -----------------------------------------------------------------------------
def load_real_data(csv_dir: str) -> Dict[str, pd.DataFrame]:
    """
    Load real customer-related data from CSV files and add surrogate keys.

    Args:
        csv_dir (str): Directory containing input CSV files.

    Returns:
        Dict[str, pd.DataFrame]: Dictionary of DataFrames for each table.
    """
    df_email = pd.read_csv(os.path.join(csv_dir, INPUT_EMAIL))
    df_phone = pd.read_csv(os.path.join(csv_dir, INPUT_PHONE))
    df_address = pd.read_csv(os.path.join(csv_dir, INPUT_ADDRESS))

    # Add surrogate keys
    df_email = df_email.assign(Email_ID=lambda df: range(1, len(df) + 1))
    df_phone = df_phone.assign(Phone_ID=lambda df: range(1, len(df) + 1))
    df_address = df_address.assign(Address_ID=lambda df: range(1, len(df) + 1))

    # Build minimal customer table from unique IDs
    customers = pd.DataFrame({'Customer_ID': df_email['Customer_ID'].unique()})

    return {
        'customer': customers,
        'customer_email': df_email,
        'customer_phone': df_phone,
        'customer_address': df_address
    }

# -----------------------------------------------------------------------------
# SYNTHETIC DATA GENERATION
# -----------------------------------------------------------------------------
def load_metadata(csv_dir: str, metadata_json: str) -> MultiTableMetadata:
    """
    Load metadata from a JSON file.

    Args:
        csv_dir (str): Directory containing metadata JSON.
        metadata_json (str): Metadata JSON filename.

    Returns:
        MultiTableMetadata: Loaded metadata object.
    """
    metadata_path = os.path.join(csv_dir, metadata_json)
    return MultiTableMetadata.load_from_json(filepath=metadata_path)

def generate_synthetic_data(
    real_data: Dict[str, pd.DataFrame],
    metadata: MultiTableMetadata,
    num_customers: int
) -> Dict[str, pd.DataFrame]:
    """
    Generate synthetic data using HMASynthesizer.

    Args:
        real_data (Dict[str, pd.DataFrame]): Real data tables.
        metadata (MultiTableMetadata): Metadata for tables.
        num_customers (int): Number of synthetic customers to generate.

    Returns:
        Dict[str, pd.DataFrame]: Synthetic data tables.
    """
    synthesizer = HMASynthesizer(metadata)
    synthesizer.fit(real_data)
    print("…fit complete, now starting sampling")
    s_start = time.time()
    synthetic_data = synthesizer.sample(num_customers)
    print(f"Sampling finished in {time.time() - s_start:.1f}s")
    return synthetic_data

# -----------------------------------------------------------------------------
# OUTPUT WRITING
# -----------------------------------------------------------------------------
def write_csvs(
    synth_data: Dict[str, pd.DataFrame],
    csv_dir: str
) -> None:
    """
    Write synthetic data tables to CSV files.

    Args:
        synth_data (Dict[str, pd.DataFrame]): Synthetic data tables.
        csv_dir (str): Output directory for CSV files.
    """
    synth_data['customer'].to_csv(os.path.join(csv_dir, OUT_CUSTOMER), index=False)
    synth_data['customer_email'].to_csv(os.path.join(csv_dir, OUT_EMAIL), index=False)
    synth_data['customer_phone'].to_csv(os.path.join(csv_dir, OUT_PHONE), index=False)
    synth_data['customer_address'].to_csv(os.path.join(csv_dir, OUT_ADDRESS), index=False)

def log_execution_time(
    start: float,
    end: float,
    csv_dir: str,
    log_filename: str = OUT_TIME_LOG
) -> None:
    """
    Log execution time to a file.

    Args:
        start (float): Start time (timestamp).
        end (float): End time (timestamp).
        csv_dir (str): Directory for log file.
        log_filename (str): Log filename.
    """
    elapsed = end - start
    with open(os.path.join(csv_dir, log_filename), 'w') as f:
        f.write(f"Execution time: {elapsed:.2f} seconds\n")

# -----------------------------------------------------------------------------
# QUALITY EVALUATION
# -----------------------------------------------------------------------------
def evaluate_synthetic_quality(
    real_data: Dict[str, pd.DataFrame],
    synthetic_data: Dict[str, pd.DataFrame],
    metadata: MultiTableMetadata
) -> dict:
    """
    Evaluate the quality of synthetic data.

    Args:
        real_data (Dict[str, pd.DataFrame]): Real data tables.
        synthetic_data (Dict[str, pd.DataFrame]): Synthetic data tables.
        metadata (MultiTableMetadata): Metadata for tables.

    Returns:
        dict: Quality report.
    """
    return evaluate_quality(real_data, synthetic_data, metadata)

# -----------------------------------------------------------------------------
# MAIN EXECUTION
# -----------------------------------------------------------------------------
def main():
    """
    Main function to orchestrate synthetic data generation and evaluation.
    """
    start_time = time.time()

    # Load real data and metadata
    real_data = load_real_data(CSV_DIR)
    metadata = load_metadata(CSV_DIR, METADATA_JSON)

    # Generate synthetic data
    synthetic_data = generate_synthetic_data(real_data, metadata, NUM_CUSTOMERS)

    # Write synthetic data to CSVs
    write_csvs(synthetic_data, CSV_DIR)

    # Evaluate quality
    quality_report = evaluate_synthetic_quality(real_data, synthetic_data, metadata)
    print("Quality Report:", quality_report)

    end_time = time.time()
    log_execution_time(start_time, end_time, CSV_DIR)

if __name__ == '__main__':
    main()