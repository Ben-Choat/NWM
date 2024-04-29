import pandas as pd
import sys

file_in = sys.argv[1]
print(f'file_in: {file_in}')
file_out = file_in.replace('.h5', '.csv')

df = pd.read_hdf(file_in)

df.to_csv(file_out)


