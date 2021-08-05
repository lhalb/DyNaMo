import pandas as pd
import numpy as np
from os import listdir
from os.path import isfile, join

mypath = "largeFiles"

onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

df = pd.DataFrame({'orig': onlyfiles})

df['name'] = range(1, len(df['orig'])+1)

print(df.head())
print(df.tail())

print('done')
