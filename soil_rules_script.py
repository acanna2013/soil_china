# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# %%
# Read in given soil data (from open source USDA)
data = pd.read_csv("Copy of soil_data.csv")

# %%
class soil_class():
    # Return the data between the PI thresholds (between lower and upper).
    def extract_pi(self, filename, lower=0, upper=float('inf')):  
        return filename[filename['PI'].between(lower, upper)]
    
    # Return the data that fits the given percentages for different soil types (A, B, C). Include margin of error of 10 as the values are not going to be exact.
    # Type A soil have equal distribution among soil, silt, clay, around 33% for each soil type.
    # Type B soil have up to 50% silt, 20% sand, 30% clay.
    # Type C soil have up to 30% silt, 60% sand, 10% clay. 
    def isInRange(self, type, val_silt, val_sand, val_clay, maxCloseness):
        if type == 'A': 
            return (abs(33-val_silt) <= maxCloseness) & (abs(33-val_sand) <= maxCloseness) & (abs(33-val_clay) <= maxCloseness)
        elif type == 'B':
            return (abs(val_silt - 50) <= maxCloseness) & (abs(val_sand - 20) <= maxCloseness) & (abs(val_clay - 30) <= maxCloseness)
        elif type == 'C':
            return (abs(val_silt - 30) <= maxCloseness) & (abs(val_sand - 60) <= maxCloseness) & (abs(val_clay - 10) <= maxCloseness)
        
    # Classifies soil data into soft vs. hard soils using Rules-based classification model. 
    def run_analysis(self, data_set):
        # Extract the necessary columns: sand, silt, clay %, PI values.
        # Ensure columns are not null
        df = data_set
        df = df[df['SAND_PCT'].notna() & df['SILT_PCT'].notna() & df['CLAY_PCT'].notna()]
        df = df[['LONGITUDE', 'LATITUDE', 'SAND_PCT', 'SILT_PCT', 'CLAY_PCT', 'PI']]

        # Filter on PI: <7 soft soil, 7-17 medium soil, >17 hard soil.
        # Note: comments that mention "additional analysis" refers to the section at the end of the function commented by "ADDITIONAL ANALYSIS" 
        soil_07 = self.extract_pi(df, 0, 7) # Classify as soft soil.
        soil_717 = self.extract_pi(df, 7, 17) # Perform additional  analysis - check type A/B/C %'s.
        soil_17 = self.extract_pi(df, lower=17) # Classify as hard soil.

        # Perform additional analysis on 7-17 as it is ambiguous.
        # Filter based on percentages of type A/B/C soils. Call the isInRange() function to extract the respective observations for each A, B, C. 
        
        # Filter on type A.
        # If true, satisfies the Type A conditions - classify as hard (type A). 
        # If false, perform additional analysis by filtering based on type B and C %s. 
        soil_717_A = soil_717
        soil_717_A['TF'] = self.isInRange('A', soil_717_A['SILT_PCT'], soil_717_A['SAND_PCT'], soil_717_A['CLAY_PCT'], 10)
        soil_717_A_hard = soil_717_A[soil_717_A['TF'] == True] # Classify as hard. 
        soil_717_A_F = soil_717_A[soil_717_A['TF'] == False] # Perform more analysis using percentages of B/C.

        # Using false values from type A, find type B.
        # If true, perform additional analysis. 
        # If false, check if it is type C. 
        soil_717_B = soil_717_A_F
        soil_717_B['TF'] = self.isInRange('B', soil_717_B['SILT_PCT'], soil_717_B['SAND_PCT'], soil_717_B['CLAY_PCT'], 10)
        soil_717_B_F = soil_717_B[soil_717_B['TF'] == False] # Perform type C percentages on it.
        soil_717_B_T = soil_717_B[soil_717_B['TF'] == True] # Perform additional analysis on it.

        # Using false values from type B, find type C.
        # If true, classify as soft as it is type C soil. 
        # If false, perform additional analysis on it.
        soil_717_C = soil_717_B_F
        soil_717_C['TF'] = self.isInRange('C', soil_717_C['SILT_PCT'], soil_717_C['SAND_PCT'], soil_717_C['CLAY_PCT'], 10)
        soil_717_C_soft = soil_717_C[soil_717_C['TF'] == True] # Classify as soft.
        soil_717_C_F = soil_717_C[soil_717_C['TF'] == False] # Perform additional analysis on it.


        # ADDITIONAL ANALYSIS 
        # If sand % > clay % or silt % > clay % significantly, then it's soft soil.
        # Otherwise, it's hard soil. 
        soil_717_B_T['TF'] = (soil_717_B_T['SAND_PCT'] > soil_717_B_T['CLAY_PCT']) | (soil_717_B_T['SILT_PCT'] > soil_717_B_T['CLAY_PCT'])
        soil_717_B_T_soft = soil_717_B_T[soil_717_B_T['TF'] == True] # Classify as soft.
        soil_717_B_T_hard = soil_717_B_T[soil_717_B_T['TF'] == False] # Classify as hard.

        soil_717_C_F['TF'] = (soil_717_C_F['SAND_PCT'] > soil_717_C_F['CLAY_PCT']) | (soil_717_C_F['SILT_PCT'] > soil_717_C_F['CLAY_PCT'])
        soil_717_C_F_soft = soil_717_C_F[soil_717_C_F['TF'] == True] # Classify as soft.
        soil_717_C_F_hard = soil_717_C_F[soil_717_C_F['TF'] == False] # Classify as hard.

        # Concatenate the dfs that contain soft soils into one dataframe.
        soft_df = pd.concat([soil_717_C_soft, soil_717_B_T_soft, soil_717_C_F_soft, soil_07])
        soft_df = soft_df.drop('TF', axis=1) # Drop the TF column as it is irrelevant. 

        # Do the same for hard soils. 
        hard_df = pd.concat([soil_717_A_hard, soil_717_B_T_hard, soil_717_C_F_hard, soil_17])
        hard_df = hard_df.drop('TF', axis=1)
        return [hard_df, soft_df]
    # End of run_analysis().

test_class = soil_class()
df = test_class.run_analysis(data)
hard_soil, soft_soil = df[0], df[1] # Extract the hard soil from first index. Extract the soft soil from second index.

# %%
hard_soil.head()

# %%
soft_soil.head()

# %%
hard_soil.to_csv('hard_soil.csv')
soft_soil.to_csv('soft_soil.csv')


