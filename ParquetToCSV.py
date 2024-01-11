import pandas as pd
import sys

# input parquet file
par_file = sys.argv[1]

# read in to data frame
df = pd.read_parquet(par_file)

# strip par_file name of .parquet and add csv
csv_file = par_file.replace('parquet', 'csv')

# write df to csv
df.to_csv(csv_file, index = False)

# print first 10 rows and columns of df
print(df.iloc[0:10, 0:10])




