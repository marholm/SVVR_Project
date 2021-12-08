import numpy as np
import pandas as pd


### input parameters ###
input_file = 'case1_T1_post_tumormask.raw'
input_file2 = 'case1_T1_post_tumormask.txt'
csv_output = 'T1_post_tumormask.csv'

dimensions = (44, 43, 19, 1)
data_type = np.uint8   # how to include little endian?

##########################


# read binary file
voxels = np.fromfile(input_file, dtype=data_type)
voxels = voxels.reshape(dimensions)
# print(voxels)

# read matrix file
matrix = np.loadtxt(input_file2, skiprows=1)
# print(matrix)

# modified from https://stackoverflow.com/questions/45855904/convert-numpy-array-with-indices-to-a-pandas-dataframe
df_voxels = pd.DataFrame(np.hstack((np.indices(voxels.shape).reshape(4, voxels.size).T, voxels.reshape(-1, 1))), columns=['x', 'y', 'z', 't', 'value'])
# print(df_voxels)

# list of lists data 
# (instead of growing a df, see https://stackoverflow.com/questions/13784192/creating-an-empty-pandas-dataframe-then-filling-it)
data = []

df_dict = df_voxels.to_dict('records')
for row_dict in df_dict:
    row = list(row_dict.values())
    data.append(np.append(np.dot(matrix, row[:-1]), row[-1]))

df_coords = pd.DataFrame(data, columns=['x', 'y', 'z', 't', 'value'])
print(df_coords)

df_coords.to_csv(csv_output, index=False)