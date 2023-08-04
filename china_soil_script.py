# %%
import pandas as pd

# %%
df_chn = pd.read_csv('china_profile.csv')
df_attr = pd.read_csv('RepresentativeHorizonValues.csv')


# %%
df_chn_attr = pd.merge(df_chn, df_attr, on=['PRID'])

# %%
df_chn_attr.columns

# %%
chn_final = df_chn_attr[['PRID', 'PDID', 'LATI', 'LNGI', 'SDTO', 'STPC', 'CLPC']]

# %%
chn_final.dropna(subset=['SDTO', 'STPC', 'CLPC'], inplace=True)
chn_final.head()

# %%
chn_final

# %%
chn_final['LAT'] = chn_final['LATI']
chn_final['LONG'] = chn_final['LNGI']
chn_final['SAND_PCT'] = chn_final['SDTO']
chn_final['SILT_PCT'] = chn_final['STPC']
chn_final['CLAY_PCT'] = chn_final['CLPC']

# %%
chn_final

# %%
import plotly.express as px

# create map of china map 
fig = px.scatter_mapbox(chn_final, 
                        lat="LAT", 
                        lon="LONG",
                        hover_data=["SAND_PCT", "SILT_PCT", 'CLAY_PCT'])

# change layout
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

# export china map to an interactive html file
fig.write_html("china_map_soil.html")

# %%
def isInRange(type, val_silt, val_sand, val_clay, maxCloseness):
    if type == 'A': 
        return (abs(33-val_silt) <= maxCloseness) & (abs(33-val_sand) <= maxCloseness) & (abs(33-val_clay) <= maxCloseness)
    elif type == 'B':
        return (abs(val_silt - 50) <= maxCloseness) & (abs(val_sand - 20) <= maxCloseness) & (abs(val_clay - 30) <= maxCloseness)
    elif type == 'C':
        return (abs(val_silt - 30) <= maxCloseness) & (abs(val_sand - 60) <= maxCloseness) & (abs(val_clay - 10) <= maxCloseness)

# %%
# A
chn_final_A = chn_final
chn_final_A['TF'] = isInRange('A', chn_final['SILT_PCT'], chn_final['SAND_PCT'], chn_final['CLAY_PCT'], 10)
chn_final_hard = chn_final_A[chn_final_A['TF'] == True] # Classify as hard. 
chn_final_F = chn_final[chn_final['TF'] == False]

# B
chn_final_B = chn_final_F
chn_final_B['TF'] = isInRange('B', chn_final_B['SILT_PCT'], chn_final_B['SAND_PCT'], chn_final_B['CLAY_PCT'], 10)
chn_final_B_F = chn_final_B[chn_final_B['TF'] == False] # Perform type C percentages on it.
chn_final_B_T = chn_final_B[chn_final_B['TF'] == True] # Perform additional analysis on it.

# C
chn_final_C = chn_final_B_F
chn_final_C['TF'] = isInRange('C', chn_final_C['SILT_PCT'], chn_final_C['SAND_PCT'], chn_final_C['CLAY_PCT'], 10)
chn_final_C_soft = chn_final_C[chn_final_C['TF'] == True] # Classify as soft.
chn_final_C_F = chn_final_C[chn_final_C['TF'] == False] # Perform additional analysis on it.

# ADDITIONAL ANALYSIS 
# If sand % > clay % or silt % > clay % significantly, then it's soft soil.
# Otherwise, it's hard soil. 
chn_final_B_T['TF'] = (chn_final_B_T['SAND_PCT'] > chn_final_B_T['CLAY_PCT']) | (chn_final_B_T['SILT_PCT'] > chn_final_B_T['CLAY_PCT'])
chn_final_B_T_soft = chn_final_B_T[chn_final_B_T['TF'] == True] # Classify as soft.
chn_final_B_T_hard = chn_final_B_T[chn_final_B_T['TF'] == False] # Classify as hard.

chn_final_C_F['TF'] = (chn_final_C_F['SAND_PCT'] > chn_final_C_F['CLAY_PCT']) | (chn_final_C_F['SILT_PCT'] > chn_final_C_F['CLAY_PCT'])
chn_final_C_F_soft = chn_final_C_F[chn_final_C_F['TF'] == True] # Classify as soft.
chn_final_C_F_hard = chn_final_C_F[chn_final_C_F['TF'] == False] # Classify as hard.

# Concatenate the dfs that contain soft soils into one dataframe.
soft_df = pd.concat([chn_final_C_soft, chn_final_B_T_soft, chn_final_C_F_soft])
soft_df = soft_df.drop('TF', axis=1) # Drop the TF column as it is irrelevant. 

# Do the same for hard soils. 
hard_df = pd.concat([chn_final_hard, chn_final_B_T_hard, chn_final_C_F_hard])
hard_df = hard_df.drop('TF', axis=1)

soft_df['CLASS'] = 'Soft'
hard_df['CLASS'] = 'Hard'

# %%
df_chn_final = pd.concat([soft_df, hard_df], ignore_index=True, sort=False)
df_chn_final.drop_duplicates(['LAT', 'LONG'], inplace=True)
df_chn_final.sort_values('PRID', inplace=True)
df_chn_final.drop(['LATI', 'LNGI', 'SDTO', 'STPC', 'CLPC'], axis=1, inplace=True)
df_chn_final.head()

# %%
df_chn_final.to_csv('china_soil.csv')

# %%
import plotly.express as px

# create map of china map 
fig = px.scatter_mapbox(df_chn_final, 
                        lat="LAT", 
                        lon="LONG",
                        color='CLASS',
                        hover_data=["SAND_PCT", "SILT_PCT", 'CLAY_PCT'])

# change layout
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

# export china map to an interactive html file
fig.write_html("china_map_soil.html")


