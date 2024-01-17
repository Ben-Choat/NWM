import netCDF4 as nc
import pandas as pd
import os

def csv_to_nc(csv_folder, nc_filename):

    nc_data_types = {
            'int64': 'i8',
            'float64': 'f8',
            'object': 'S1',
            'datetime64[ns]': 'S1'
            }
    # Get a list of CSV files in the folder
    csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]

    # Create a NetCDF file
    with nc.Dataset(nc_filename, 'w') as dataset:
        # Create the dimensions
        dataset.createDimension('time', None)
        dataset.createDimension('catchment_id', len(csv_files))
        dataset.createDimension('str_dim', 1)

        # Create variables
        ids_variable = dataset.createVariable('ids', 'S1', ('catchment-id', 'str_dim'))
        time_variable = dataset.createVariable('Time', 'f8', ('catchment-id', 'time'))
        catchment_id_variable = dataset.createVariable('catchment-id', 'S1', ('catchment-id', 'str_dim'))

        # Create a variable for the 'ids'
#         ids_variable = dataset.createVariable('ids', 'S1', ('row',))

        # Iterate through CSV files
        for i, csv_file in enumerate(csv_files[0:3]):
            # Extract ID from the filename (assuming the filename is 'id_<ID>.csv')
            file_id = csv_file.split('-')[1].split('.')[0]

            # Read CSV into a Pandas DataFrame
            df = pd.read_csv(os.path.join(csv_folder, csv_file), 
                    dtype = {'SWDOWN': str}, parse_dates = ['Time'])
            df['SWDOWN'] = df['SWDOWN'].astype(float)

            # Write the 'ids' variable for each row in the CSV
            # ids_variable[len(ids_variable):] = [file_id] * len(df)

            # write ids variable
            ids_variable[i, 0] = file_id.encode('utf-8')

            # write 'Time' variable
            time_variable[i, :] = df['Time'].values.astype('



#            print(df.head())
#             print(df['Time'].astype(str))

            # Create a variable for each column in the CSV
            for col_name in df.columns:
                variable_name = col_name
                data_type = str(df[col_name].dtype)
#                 print(data_type)
                if data_type == 'datetime64[ns]':
                    df[col_name] = df[col_name].astype(str)

                # get nc data type, and return S1 if not included in dict
                nc_data_type = nc_data_types.get(data_type, 'S1')

                # if variable not created in nc dataset yet, create it
                if not variable_name in dataset.variables:
                    dataset.createVariable(variable_name, nc_data_type, ('row',))
                dataset[variable_name][len(dataset[variable_name]):] = df[col_name].values

            # Create a variable for the ID
#             dataset.createVariable(f"id_{file_id}", 'S1', ('row',))
#             dataset[f"id_{file_id}"][:] = file_id.encode('utf-8')

# Example usage
csv_folder_path = 'forcing/'
nc_file_path = 'forcing_new.nc'
csv_to_nc(csv_folder_path, nc_file_path)
