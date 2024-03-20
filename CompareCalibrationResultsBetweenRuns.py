
# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px


# %%
df1 = pd.read_excel(
    'C:/Projects/NOAA_NWM/MISCFiles/NWM_performance_first.xlsx',
    dtype={'hru_id_CAMELS': 'str'}
)

df2 = pd.read_excel(
    'C:/Projects/NOAA_NWM/MISCFiles/NWM_performance_second.xlsx',
    dtype={'hru_id_CAMELS': 'str'}
)

df_attr = pd.read_csv(
    'C:/Projects/NOAA_NWM/MISCFiles/camels_topo.txt',
    sep=';',
    dtype={'gauge_id': str}
)

df_NCat = pd.read_csv(
    'C:/Projects/NOAA_NWM/MISCFiles/AllBasins2022-12-061248.csv',
    # usecols = ['hru_id_CAMELS', 'NCat', 'N_nexus', 'aridity', 'p_seasonality', 'frac_snow'],
    dtype={'hru_id_CAMELS': 'str'}
)
'''
Catchment 13235000 was not included in our original calibrations, but has
152 catchments, so I'm going to use it in testing parallelization.
'''
####################

dftm1 = df1.query("Model_RR == 'Topmodel'")
dftm2 = df2.query("Model_RR == 'Topmodel'")

###################

df1.groupby('Model_RR')['KGE'].count()
df2.groupby('Model_RR')['KGE'].count()

'''
The NWM_performance_first.xlsx file from 1st calibrations has 98 results for
topmodel, CFE, and NWM2.1 and 96 for CFE_X.
The NWM_performance_first.xlsx file from 2nd calibrations has 93 results for
CFE and NWM2.1, 92 for topmodel, and 91 for CFE_X.

There was one catchment that I did not have observations for, so I skipped it
when rerunning TOPMODEL.
'''

dftm = pd.merge(dftm1, dftm2, 
                on = ['hru_id_CAMELS', 'Model_RR'], 
                # how = 'left',
                suffixes=['_1', '_2'])
dftm = pd.merge(dftm, df_attr, 
                left_on = 'hru_id_CAMELS',
                right_on = 'gauge_id',
                how = 'left')
dftm = pd.merge(dftm, df_NCat,
                on = 'hru_id_CAMELS',
                how='left')

dftm_poor = dftm.query('KGE_1 < 0 & KGE_2 < 0')
dftm_good = dftm.query('KGE_1 > 0.65 & KGE_2 > 0.65')
dftm_1g2p = dftm.query('KGE_1 > 0.65 & KGE_2 < 0.5')
dftm_1p2g = dftm.query('KGE_1 < 0.5 & KGE_2 > 0.65')
dftm_1better = dftm.query('KGE_1 > KGE_2')
dftm_2better = dftm.query('KGE_2 > KGE_1')
dftm_1eq2 = dftm.query('KGE_1 == KGE_2')


# %% #########################

# plt.hist(dftm['KGE_1'], bins=100)
# plt.xlim([-1, 1])

# %%
ax = sns.ecdfplot(dftm['KGE_1'], label='1st')
sns.ecdfplot(dftm['KGE_2'], ax = ax, label='2nd')
ax.set_xlim([-1, 1])
ax.legend()
ax.grid()
ax.set(xlabel='KGE')
plt.show()

# %%

ax = sns.scatterplot(data=dftm, x='KGE_1', y='KGE_2', hue='area_gages2')
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.plot([-1, 1], [-1, 1], color = 'red', linestyle = '--')
ax.grid()
plt.show()

# %% same as previous except in ploty express

fig = px.scatter(
    dftm,
    x='KGE_1',
    y='KGE_2',
    color='area_gages2',
    range_x=[-1, 1],
    range_y=[-1, 1],
    labels={'KGE_1', 'KGE_2'},
    title='Calib R2 vs R1 - TOPMODEL',
    hover_data=['hru_id_CAMELS', 'area_gages2']
)

# fig = go.Figure()

# scatter = go.Scatter(
#     x=dftm['KGE_1'],
#     y=dftm['KGE_2'],
#     mode='markers',
#     marker=dict(color=dftm['area_gages2']),
#     customdata=np.stack((dftm['hru_id_CAMELS'], dftm['area_gages2']), axis=1),

#     # text=dftm['hru_id_CAMELS'],
#     # hoverinfo='text',
# )


# fig.add_trace(scatter)

fig.update_layout(
    xaxis=dict(range=[-1, 1]),
    yaxis=dict(range=[-1, 1]),
    title='Calib R2 vs R1 - TOPMODEL',
    xaxis_title='KGE_1',
    yaxis_title='KGE_2',
)

fig.update_coloraxes(colorbar={"len": 0.6})

fig.add_trace(go.Scatter(
    x=dftm_1g2p['KGE_1'], y=dftm_1g2p['KGE_2'],
    mode="markers",
    marker={"symbol": "circle-open","color":'cyan'}, 
    name="1g2p",
    customdata=np.stack((dftm_1g2p['hru_id_CAMELS'], dftm_1g2p['area_gages2']), axis=1)
))

fig.add_trace(go.Scatter(
    x=dftm_1p2g['KGE_1'], y=dftm_1p2g['KGE_2'],
    mode="markers",
    marker={"symbol": "circle-open","color":'lime'}, 
    name="1p2g",
    customdata=np.stack((dftm_1p2g['hru_id_CAMELS'], dftm_1p2g['area_gages2']), axis=1)
))

# Add a diagonal line
fig.add_shape(type='line',
              x0=-1, y0=-1, x1=1, y1=1,
              line={"color": "red", "dash": "dash"})
# Set aspect ratio to make the plot square
fig.update_layout(
    autosize=False,
    width=800,  # Adjust the width as needed
    height=700  # Adjust the height as needed
)

fig.update_traces(
    hovertemplate='ID: %{customdata[0]}\
        <br>Area: %{customdata[1]}',
    # colorbar={"len": 0.75}
    )

# Show the plot
fig.show()

# fig.write_html('C:/Projects/NCPA_CloudSeeding/GroundBased/Figs/CompareKGEs.html')

# subset to id'd catchments
catch_use1g2p = ['01532000', '07195800', '11476600']
catch_use1p2g = ['01435000', '01550000']
catch_small = ['02430085', '10259000']
catch_Usepp = ['06479215']
df_out = dftm.query("hru_id_CAMELS in @catch_use1g2p or hru_id_CAMELS in @catch_use1p2g\
                    or hru_id_CAMELS in @catch_small or hru_id_CAMELS in @catch_Usepp")

# df_out.to_csv('C:/Projects/NOAA_NWM/MISCFiles/TM_CalibTestCatchments.csv',
#               index=False)


# %%

df_plot = dftm.melt(id_vars='hru_id_CAMELS', value_vars=['KGE_1', 'KGE_2'], value_name='KGE')
ax = sns.boxplot(data=df_plot, y='KGE', x = 'variable')
plt.show()




# %% ID catchment with large NCat for testing parallelism
####################################
dftm['NCat'].hist(bins=25)

dftm_g40 = dftm.query("NCat > 40").sort_values(by = ['NCat', 'KGE_1', 'KGE_2']) # [
    # ['hru_id_CAMELS', 'Folder_CAMELS', 'NCat', 'N_nexus', 'KGE_1', 'KGE_2']
    # ].sort_values(by = ['NCat', 'KGE_1', 'KGE_2'])
dftm_g60 = dftm.query("NCat > 60").sort_values(by = ['NCat', 'KGE_1', 'KGE_2']) # [
    # ['hru_id_CAMELS', 'Folder_CAMELS', 'NCat', 'N_nexus', 'KGE_1', 'KGE_2']
    # ].sort_values(by = ['NCat', 'KGE_1', 'KGE_2'])
dftm_g80 = dftm.query("NCat > 80").sort_values(by = ['NCat', 'KGE_1', 'KGE_2']) # [
    # ['hru_id_CAMELS', 'Folder_CAMELS', 'NCat', 'N_nexus', 'KGE_1', 'KGE_2']
    #

dftm_parTest = dftm_g40.query(
    "hru_id_CAMELS in ['11176400', '06903400', '01543000']"
)

'''
from dftm_g40 - use 11176400 (NCat=44; KGE_1=0.465034; KGE_2=0.258057)
from dftm_g60 - use 06903400 (NCat=62; KGE_1=0.615689; KGE_2=-0.031818)
from dftm_g80 - use 01543000 (NCat=89; KGE_1=0.623558; KGE_2=0.441164)
'''

# dftm_parTest.to_csv('C:/Projects/NOAA_NWM/MISCFiles/ParallelTestCatchments.csv',
#               index=False)


# %% hold

'''
Catchment 13235000 was not included in our original calibrations, but has
152 catchments, so I'm going to use it in testing parallelization.
'''

df_NCatTest = df_NCat.query("hru_id_CAMELS == '13235000'")
df_NCatTest = pd.merge(df_NCatTest, df_attr, 
                       left_on = 'hru_id_CAMELS', right_on = 'gauge_id')

# dftm_parTest2 = pd.concat([dftm_parTest, df_NCatTest], axis = 0)

# dftm_parTest2.loc[dftm_parTest2['hru_id_CAMELS'] == '13235000', ]

# df_NCatTest.to_csv(
#     'C:/Projects/NOAA_NWM/MISCFiles/ParallelTestCatchment_13235000.csv',
#       index=False
# )


# %%
