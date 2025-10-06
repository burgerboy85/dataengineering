
"""
synthetic_data_generator.py
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


Generate synthetic customer, email, phone and address tables using
SDV's HMASynthesizer, preserving referential integrity,
and write them out as CSVs for testing.
"""

import os
import time
import logging
import pandas as pd
from sdv.metadata.multi_table import MultiTableMetadata
from sdv.multi_table import HMASynthesizer
from sdv.evaluation.multi_table import evaluate_quality
from sdv.metadata import Metadata

# -----------------------------------------------------------------------------
# CONFIGURATION (edit paths or number of customers as needed)
# -----------------------------------------------------------------------------
NUM_CUSTOMERS = 10
CSV_DIR       = '/Users/rahulchakraborty/Documents/Study/Data_Engineering/my_project/data/customer'   # directory for input real CSVs and output synthetic CSVs


INPUT_EMAIL   = 'customer_email_details.csv'
INPUT_PHONE   = 'customer_phone_details.csv'
INPUT_ADDRESS = 'customer_address_details.csv'

OUT_CUSTOMER  = 'synthetic_customer.csv'
OUT_EMAIL     = 'synthetic_customer_email.csv'
OUT_PHONE     = 'synthetic_customer_phone.csv'
OUT_ADDRESS   = 'synthetic_customer_address.csv'
OUT_TIME_LOG  = 'execution_time.txt'

# -----------------------------------------------------------------------------
# LOAD & PREP REAL DATA
# -----------------------------------------------------------------------------
def load_real_data():
    df_email   = pd.read_csv(os.path.join(CSV_DIR, INPUT_EMAIL))
    df_phone   = pd.read_csv(os.path.join(CSV_DIR, INPUT_PHONE))
    df_address = pd.read_csv(os.path.join(CSV_DIR, INPUT_ADDRESS))

    # Add surrogate keys
    df_email   = df_email.assign(Email_ID=lambda df: range(1, len(df) + 1))
    df_phone   = df_phone.assign(Phone_ID=lambda df: range(1, len(df) + 1))
    df_address = df_address.assign(Address_ID=lambda df: range(1, len(df) + 1))

    # Build minimal customer table from unique IDs
    customers = pd.DataFrame({'Customer_ID': df_email['Customer_ID'].unique()})
    

    return {
        'customer':         customers,
        'customer_email':   df_email,
        'customer_phone':   df_phone,
        'customer_address': df_address
    }

# -----------------------------------------------------------------------------
# SYNTHESIS
# -----------------------------------------------------------------------------
def generate_synthetic(real_data, num_customers):
    
    # Alternatively, you can use MultiTableMetadata if you have multiple tables
    #metadata = MultiTableMetadata()
    #metadata.detect_from_dataframes(real_data)
    #metadata.save_to_json(filepath='/Users/rahulchakraborty/Documents/Study/Data_Engineering/my_project/data/customer/my_metadata_v1.json')
    metadata = MultiTableMetadata.load_from_json(filepath='/Users/rahulchakraborty/Documents/Study/Data_Engineering/my_project/data/customer/my_metadata_v1.json')


    synthesizer = HMASynthesizer(metadata)
    synthesizer.fit(real_data)

    print("…fit complete, now starting sampling")

    import time
    s_start = time.time()
    print(f"Sampling finished in {time.time() - s_start:.1f}s")

    # positional argument for number of customer sequences
    synthetic_data = synthesizer.sample(num_customers)
    return synthetic_data, metadata

# -----------------------------------------------------------------------------
# WRITE CSV OUTPUT
# -----------------------------------------------------------------------------
def write_csvs(synth_data):
    synth_data['customer'].to_csv(os.path.join(CSV_DIR, OUT_CUSTOMER), index=False)
    synth_data['customer_email'].to_csv(os.path.join(CSV_DIR, OUT_EMAIL), index=False)
    synth_data['customer_phone'].to_csv(os.path.join(CSV_DIR, OUT_PHONE), index=False)
    synth_data['customer_address'].to_csv(os.path.join(CSV_DIR, OUT_ADDRESS), index=False)


# -----------------------------------------------------------------------------
# LOG EXECUTION TIME
# -----------------------------------------------------------------------------
def log_time(start, end):
    elapsed = end - start
    with open(os.path.join(CSV_DIR, OUT_TIME_LOG), 'w') as f:
        f.write(f"Execution time: {elapsed:.2f} seconds\n")

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
def main():
    start_time = time.time()

    real = load_real_data()
    synthetic, metadata = generate_synthetic(real, NUM_CUSTOMERS)
    write_csvs(synthetic)

    # Evaluate quality after generating synthetic data
    quality_report = evaluate_quality(
        real,
        synthetic,
        metadata
    )
    print("Quality Report:", quality_report)

    end_time = time.time()
    log_time(start_time, end_time)
    log_time(start_time, end_time)


if __name__ == '__main__':
    main()