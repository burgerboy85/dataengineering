#import pandas as pd
import fireducks.pandas as pd
import numpy as np
import time

# File path
file_path = "/Users/rahulchakraborty/Documents/dbt_tutorial/course/dbttutorial/hollywood_movies.csv"



# Read and group by using fireducks
start_time = time.time()
df_fireducks = pd.read_csv(file_path)
fireducks_read_time = time.time() - start_time
grouped_fireducks = df_fireducks.groupby('release_year').size()
fireducks_time = time.time() - start_time

# Print results
#print("Fireducks GroupBy Result:")
#print(grouped_fireducks)


print(f"fireducks Read Time to Read 1GB File: {fireducks_read_time:.4f} seconds")
print(f"fireducks Time to perform Group By on 1 GB File: {fireducks_time:.4f} seconds")

#speed_up = pandas_time / fireducks_time
#print(f"FireDucks is approximately {speed_up:.2f} times faster than pandas.")