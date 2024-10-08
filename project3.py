import math
import os, sys
import pandas as pd
import numpy as np
sys.path.append(os.path.abspath(os.path.join('modulos')))
from estrategia1 import *
from estrategia2 import *
from estrategia3 import *

## Telemarketing Data

## Exploratory Analysis

## some Pandas configs 
pd.set_option('display.max_columns', None) 
# pd.set_option('display.expand_frame_repr', False) 

config_na = ['n/a', 'na', 'undefined'] #defining more names to pandas recognize as missing value
dataset = pd.read_csv(r'C:\Users\leand\OneDrive\Documentos\FormacaoDSA\f_project3\Scripts-P3\dados\dataset.csv', na_values=config_na) #in addition to the default values of na_values, recognize the values of list too
# print(dados.head())

dictionary = pd.read_excel(r'C:\Users\leand\OneDrive\Documentos\FormacaoDSA\f_project3\Scripts-P3\dados\Dicionario.xlsx')
# print(dados_desc.head())

both = pd.concat([pd.Series(dataset.columns.tolist()), dictionary['Fields']],axis=1).rename(columns={0:'Dataset', 'Fields': 'Dicionario'}, inplace=True)  #pd.series define a one-column dataframe(in the case, is one column of all columns of dataset) and concat is like a merge these two columns. And apply a simple rename 
# print(both)

##fix the divergence between the informations of dictionary and dataset
# print(dataset[['Dur. (ms).1', 'Dur. (ms)']])
dataset.rename(columns={'Dur. (ms)': 'Dur. (s)',
                        'Dur. (ms).1':'Dur. (ms)',
                        'Start ms': 'Start Offset (ms)',
                        'End ms': 'End Offset (ms)'}, inplace=True)
# print(dataset.info())
# print(dataset.describe())


## Data Cleaning
# print(help(func_calc_percentual_valores_ausentes))
# func_calc_percentual_valores_ausentes(dataset)

## remove columns with 30% of missing values
df_missing = func_calc_percentual_valores_ausentes_coluna(dataset)
# print(df_missing)
col_removed = df_missing[df_missing['% de Valores Ausentes'] >= 30.00].index.tolist() 
col_removed = [i for i in col_removed if i not in ['TCP UL Retrans. Vol (Bytes)', 'TCP DL Retrans. Vol (Bytes)']]
dataset_clean = dataset.drop(col_removed, axis=1)
# print(dataset_clean.shape)

# func_calc_percentual_valores_ausentes(dataset_clean)
# print('---------------------')
# df_dataset_clean = func_calc_percentual_valores_ausentes_coluna(dataset_clean)
# print(df_dataset_clean)

## Apply method filling regressive in specific numerical columns
fix_missing_bfill(dataset_clean, 'TCP UL Retrans. Vol (Bytes)')
print('---------------------')
fix_missing_bfill(dataset_clean, 'TCP DL Retrans. Vol (Bytes)')


## Verify if is possible fill missing values with  average of columns
## Template:
## if asymmetry is between -0,5 and 0,5, the data is very symmetrical
## if asymmetry is between -1,0 and -0,5 or between 0,5 e 1,0, the data is moderately symmetrical
## if asymmetry is less than -1,0 or greater than 1, the data is highly biased (enviesados)

# print(dataset_clean['Avg RTT DL (ms)'].skew(skipna=True))
# print('---------------')
# print(dataset_clean['Avg RTT UL (ms)'].skew(skipna=True))
## Result:
## highly biased. Now we can continue with progressive filling 

fix_missing_ffill(dataset_clean, 'Avg RTT DL (ms)')
fix_missing_ffill(dataset_clean, 'Avg RTT UL (ms)')

# df_dataset_clean = func_calc_percentual_valores_ausentes_coluna(dataset_clean)
# print(df_dataset_clean)

## Categorical variables to be fixed
fix_missing_value(dataset_clean, 'Handset Type', 'unknown')
fix_missing_value(dataset_clean, 'Handset Manufacturer', 'unknown')
# func_calc_percentual_valores_ausentes_linha(dataset_clean)

drop_rows_with_missing_values(dataset_clean)
# func_calc_percentual_valores_ausentes_linha(dataset_clean)

## Convert data types
# print(dataset_clean.dtypes)
# print(dataset_clean.head())
convert_to_datetime(dataset_clean, ['Start','End'])  

str_cols = dataset_clean.select_dtypes(include='object').columns.tolist()
convert_to_string(dataset_clean, str_cols)

int_cols = ['Bearer Id', 'IMSI', 'MSISDN/Number', 'IMEI']
convert_to_int(dataset_clean, int_cols)

# print(dataset_clean.columns)
# print(dataset_clean.dtypes)

## Verify value of 2 columns that looks equal
# print(dataset_clean[['Dur. (ms)', 'Dur. (s)']])
copy_dur = dataset_clean[['Dur. (ms)', 'Dur. (s)']].copy()  #df copy of two columns
multiply_by_factor(copy_dur, ['Dur. (ms)'], 1/1000)  #apply conversion (seconds to milliseconds)
copy_dur['comparison'] = (copy_dur['Dur. (ms)'] == copy_dur['Dur. (s)']).apply(math.floor)  #create new column that will compare the two columns and finally apply comparison based on floor (piso/chão, arredondando)
# print(copy_dur)
drop_columns(dataset_clean, ['Dur. (s)'])  #drop the column equal


## Outliers treatment
col_numerical = dataset_clean.select_dtypes(include='float').columns.tolist()
outliers = TrataOutlier(dataset_clean)
sergio = outliers.getOverview(col_numerical)
print(sergio.head(11))
print('----------')
outliers.replace_outliers_with_fences(col_numerical)
print('----------')
sergio = outliers.getOverview(col_numerical)
print(sergio.head(11))

# dataset_clean.to_csv('dados/dataset_clean.csv')
