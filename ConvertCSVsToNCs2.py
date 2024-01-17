import netCDF4 as nc
import pandas as pd
import os

def csv_to_nc(csv_folder, nc_filename):
    # Get a list of CSV files in the folder
    csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]

    # Create a NetCDF file
    with nc.Dataset(nc_filename, 'w', format='NETCDF4') as dataset:
        # Create dimensions
        dataset.createDimension('time', None)
        dataset.createDimension('catchment-id', len(csv_files))
        dataset.createDimension('str_dim', 1)

        # Create variables
        ids_variable = dataset.createVariable('ids', 'S1', ('catchment-id',), vlen = str)
        time_variable = dataset.createVariable('Time', 'float64', ('catchment-id', 'time'), fill_value = False)
        catchment_id_variable = dataset.createVariable('catchment-id', 'S1', ('catchment-id', 'str_dim'))

        # Iterate through CSV files
        for i, csv_file in enumerate(csv_files):
            # Extract ID from the filename (assuming the filename is 'id_<ID>.csv')
            file_id = csv_file.split('-')[1].split('.')[0]

            # Read CSV into a Pandas DataFrame
            df = pd.read_csv(os.path.join(csv_folder, csv_file), dtype={'SWDOWN': str}, parse_dates=['Time'])

            # Write 'ids' variable
            ids_variable[i] = file_id.encode('utf-8')

            # Write 'catchment-id' variable
            catchment_id_variable[i, 0] = file_id.encode('utf-8')

            # Write 'Time' variable
            time_variable[i, :] = df['Time'].values.astype('float64')

            # Create a variable for each column in the CSV
            for col_name in df.columns:
                if col_name != 'Time':
                    variable_name = col_name
                    data_type = str(df[col_name].dtype)

                    # Map Pandas data types to NetCDF data types
                    nc_data_type = {
                        'int64': 'i8',
                        'float64': 'f8',
                        'object': 'S1',
                        'datetime64[ns]': 'f8',  # Convert datetime to float64 for NetCDF
                    }.get(data_type, 'S1')

                    # Convert datetime values to float64
                    if data_type == 'datetime64[ns]':
                        df[col_name] = df[col_name].values.astype('float64')

                    # Create a variable for each column
                    if not variable_name in dataset.variables:
                        dataset.createVariable(variable_name, nc_data_type, ('catchment-id', 'time'))
                    dataset[variable_name][i, :] = df[col_name].values

# Example usage
csv_folder_path = './forcing'
nc_file_path = 'forcing_new.nc'
csv_to_nc(csv_folder_path, nc_file_path)

# Printing dimensions
#print("Dimensions:")
#for dim_name, dim_obj in dataset.dimensions.items():
#    print(f"{dim_name}: {dim_obj}")
#
## Printing variables
#print("\nVariables:")
#for var_name, var_obj in dataset.variables.items():
#    print(f"{var_name}: {var_obj}")
#
