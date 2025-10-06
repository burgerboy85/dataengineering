import pandas as pd 
import time
from sdv.single_table import GaussianCopulaSynthesizer 
from sdv.metadata import SingleTableMetadata 
from sdv.evaluation.single_table import run_diagnostic 
from sdv.evaluation.single_table import evaluate_quality

#This constraint ensures that the 'Date Of Account Opening' is always before the 'Last Transaction Date' for each customer.
my_constraint = {
    'constraint_class': 'Inequality',
    'constraint_parameters': {
        'low_column_name': 'dob',
        'high_column_name': 'account_open_date',
        'strict_boundaries': True
    }
}


#Assume 'real_data' is your original dataset 
#real_data = pd.read_csv('/Users/rahulchakraborty/Documents/Study/GenAI/my_project/data/Comprehensive_Banking_Database.csv') 
real_data = pd.read_csv('/Users/rahulchakraborty/Documents/dbt_tutorial/dbt_handson/customer_master.csv')
#real_data = pd.read_csv('/Users/rahulchakraborty/Documents/dbt_tutorial/dbt_handson/customer_transactions.csv')
#real_data = pd.read_csv('/Users/rahulchakraborty/Documents/dbt_tutorial/dbt_handson/branch_info.csv')



#generate metadata 
metadata = SingleTableMetadata() 
metadata.detect_from_dataframe(real_data) 

#correct metadata to use the same values as in the real data 
metadata.update_column(column_name='customer_id', sdtype='id')
metadata.update_column(column_name='full_name', sdtype='categorical')
metadata.update_column(column_name='dob', sdtype='datetime')
metadata.update_column(column_name='gender', sdtype='categorical')
metadata.update_column(column_name='kyc_status', sdtype='categorical')
metadata.update_column(column_name='account_open_date', sdtype='datetime')
metadata.update_column(column_name='branch_id', sdtype='categorical')

#save metadata to json 
metadata.save_to_json('/Users/rahulchakraborty/Documents/Study/GenAI/my_project/data/cust_master_metadata_test.json')
#metadata.save_to_json('/Users/rahulchakraborty/Documents/Study/GenAI/my_project/data/cust_trans_metadata_test.json')
#metadata.save_to_json('/Users/rahulchakraborty/Documents/Study/GenAI/my_project/data/branch_info_metadata_test.json')


#from sdv.single_table import GaussianCopulaSynthesizer 
#Step 1: Create the synthesizer 
synthesizer = GaussianCopulaSynthesizer(metadata) 

synthesizer.add_constraints(constraints=[
    my_constraint
])

#Step 2: Train the synthesizer 
synthesizer.fit(real_data)

#Step 3: Generate synthetic data 
start_time = time.time()

synthetic_data = synthesizer.sample(num_rows=100000) 
#print(synthetic_data.head(10))

end_time = time.time()
print(f"Time taken to generate synthetic data: {end_time - start_time} seconds")

#save the data as a CSV 
synthetic_data.to_csv('/Users/rahulchakraborty/Documents/Study/GenAI/my_project/data/cust_master_output_synthetic_data.csv', index=False)
#synthetic_data.to_csv('/Users/rahulchakraborty/Documents/Study/GenAI/my_project/data/cust_transactions_output_synthetic_data.csv', index=False)
#synthetic_data.to_csv('/Users/rahulchakraborty/Documents/Study/GenAI/my_project/data/branch_info_output_synthetic_data.csv', index=False)

# Step 4: Evaluate the quality of the synthetic data
from sdv.evaluation.single_table import run_diagnostic, evaluate_quality


# 1. perform basic validity checks
diagnostic = run_diagnostic(real_data, synthetic_data, metadata)

# 2. measure the statistical similarity
quality_report = evaluate_quality(real_data, synthetic_data, metadata)
