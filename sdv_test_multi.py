#!/usr/bin/env python3
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
import pandas as pd
from sdv.metadata.multi_table import MultiTableMetadata
from sdv.multi_table import HMASynthesizer
from sdv.evaluation.multi_table import evaluate_quality


# -----------------------------------------------------------------------------
# CONFIGURATION (edit paths or number of customers as needed)
# -----------------------------------------------------------------------------
NUM_CUSTOMERS = 100
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

    # Build minimal customer table from all unique IDs in all sources
    all_customer_ids = pd.concat([
        df_email['Customer_ID'],
        df_phone['Customer_ID'],
        df_address['Customer_ID']
    ]).drop_duplicates().reset_index(drop=True)
    customers = pd.DataFrame({'Customer_ID': all_customer_ids})
    customers = customers.assign(Customer_Key=lambda df: range(1, len(df) + 1))

    # Map Customer_ID to Customer_Key for FK usage
    id_to_key = dict(zip(customers['Customer_ID'], customers['Customer_Key']))
    df_email['Customer_Key']   = df_email['Customer_ID'].map(id_to_key)
    df_phone['Customer_Key']   = df_phone['Customer_ID'].map(id_to_key)
    df_address['Customer_Key'] = df_address['Customer_ID'].map(id_to_key)

    # Ensure Customer_Key is present in all tables
    df_email['Customer_Key']   = df_email['Customer_Key'].fillna(customers['Customer_Key'].max() + 1)
    df_phone['Customer_Key']   = df_phone['Customer_Key'].fillna(customers['Customer_Key'].max() + 1)
    df_address['Customer_Key'] = df_address['Customer_Key'].fillna(customers['Customer_Key'].max() + 1)

    # Ensure all Customer_IDs and Customer_Keys are unique in the customer table
    customers = customers.drop_duplicates(subset='Customer_ID')
    customers = customers.drop_duplicates(subset='Customer_Key')

    return {
        'customer':         customers,
        'customer_email':   df_email,
        'customer_phone':   df_phone,
        'customer_address': df_address
    }
# SYNTHESIS
def generate_synthetic(real_data, num_customers):
    metadata = MultiTableMetadata.load_from_json(filepath='/Users/rahulchakraborty/Documents/Study/Data_Engineering/my_project/data/customer/my_metadata_v1.json')

    synthesizer = HMASynthesizer(metadata)
    synthesizer.fit(real_data)

    print("…fit complete, now starting sampling")

    s_start = time.time()
    # Sample the customer table first to get unique Customer_Key values
    synthetic_customers = synthesizer.sample(scale=num_customers / len(real_data['customer']))
    customer_keys = synthetic_customers['customer']['Customer_Key'].tolist()

    # Sample related tables using the sampled customer keys to maintain referential integrity
    synthetic_emails = synthesizer.sample(scale=num_customers / len(real_data['customer_email']))
    synthetic_phones = synthesizer.sample(scale=num_customers / len(real_data['customer_phone']))
    synthetic_addresses = synthesizer.sample(scale=num_customers / len(real_data['customer_address']))

    # Filter related tables to only include Customer_Key values present in synthetic_customers
    synthetic_emails['customer_email'] = synthetic_emails['customer_email'][synthetic_emails['customer_email']['Customer_Key'].isin(customer_keys)]
    synthetic_phones['customer_phone'] = synthetic_phones['customer_phone'][synthetic_phones['customer_phone']['Customer_Key'].isin(customer_keys)]
    synthetic_addresses['customer_address'] = synthetic_addresses['customer_address'][synthetic_addresses['customer_address']['Customer_Key'].isin(customer_keys)]

    synthetic_data = {
        'customer': synthetic_customers['customer'],
        'customer_email': synthetic_emails['customer_email'],
        'customer_phone': synthetic_phones['customer_phone'],
        'customer_address': synthetic_addresses['customer_address']
    }

    print(f"Sampling finished in {time.time() - s_start:.1f}s")
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