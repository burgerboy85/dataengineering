import pandas as pd
import fireducks.pandas as fr
import time

# File path
file_path = "/Users/rahulchakraborty/Documents/dbt_tutorial/course/dbttutorial/hollywood_movies.csv"

# Read and group by using pandas
start_time = time.time()
df_pandas = pd.read_csv(file_path)
pandas_read_time = time.time() - start_time
grouped_pandas = df_pandas.groupby('release_year').size()
pandas_time = time.time() - start_time

# Read and group by using fireducks
#start_time = time.time()
#df_pandas = pd.read_csv(file_path)
#grouped_fireducks = df_pandas.groupby('release_year').size()
#fireducks_time = time.time() - start_time

# Print results
#print("Pandas GroupBy Result:")
#print(grouped_pandas)
#print("Fireduck GroupBy Result:")
#print(grouped_fireducks)

print(f"Pandas Read Time to Read 1GB File: {pandas_read_time:.4f} seconds")
print(f"Pandas Time to perform Group By on 1 GB File: {pandas_time:.4f} seconds")
