import pandas as pd 
from sdv.metadata import SingleTableMetadata 
from sdv.evaluation.single_table import run_diagnostic 
from sdv.evaluation.single_table import evaluate_quality

from sdv.single_table import CopulaGANSynthesizer


#Assume 'real_data' is your original dataset 
real_data = pd.read_csv('/Users/rahulchakraborty/Documents/Study/GenAI/my_project/data/updated_product.csv') 

#generate metadata 
metadata = SingleTableMetadata() 
metadata.detect_from_csv(filepath='/Users/rahulchakraborty/Documents/Study/GenAI/my_project/data/updated_product.csv') 

# correct metadata to use the same values as in the real data 
metadata.update_column( column_name='product_id', sdtype='id' ) 
metadata.update_column( column_name='product_name', sdtype='categorical' ) 
metadata.update_column( column_name='category', sdtype='categorical' ) 


#save metadata to json 
metadata.save_to_json('metadata.json')

#Step 1: Create the synthesizer 
synthesizer = CopulaGANSynthesizer(metadata)

#Step 2: Train the synthesizer 
synthesizer.fit(real_data) 

#Step 3: Generate synthetic data 
test_synthetic_data = synthesizer.sample(num_rows=20)
print(test_synthetic_data.head(10))

#save the data as a CSV 
test_synthetic_data.to_csv('test_synthetic_data.csv', index=False)


# 1. perform basic validity checks
diagnostic = run_diagnostic(real_data, test_synthetic_data, metadata)

# 2. measure the statistical similarity
quality_report = evaluate_quality(real_data, test_synthetic_data, metadata)
