import os
from shutil import copyfile
import pandas as pd
import numpy as np
from os import listdir
from os.path import isfile, join

def make_dataframe_from_files(files):
    df = pd.DataFrame({'orig': files})

    df['name'] = range(1, len(df['orig']) + 1)

    # Erzeuge Liste auf Einzelstrings aus Dateinamen
    stringlist = [s.split('.')[0].split('_') for s in df['orig']]

    # Hole Figurtyp ab
    figtype = [s[0].split('-')[0] for s in stringlist]

    # hole Berechnungsmethode ab ab
    calctype = [s[1] for s in stringlist]

    # Erzeuge Arrays für Punkte und Größe
    pointnr = [None] * len(df['orig'])
    filesize = [None] * len(df['orig'])
    calc_size = [None] * len(df['orig'])

    for i, string in enumerate(stringlist):
        if 'size' in string:
            calc_size[i] = string[3]
        for s in string:
            if '-pkt' in s:
                pointnr[i] = s.split('-')[0]
            if '-B' in s:
                filesize[i] = s.split('-')[0]

    # Füge Spalten dem Datafram ehinzu
    df['f-type'], df['c-type'], df['points'], df['f-size'], df[
        'c-size'] = figtype, calctype, pointnr, filesize, calc_size
    # Entferne leere Zellen für Export
    df.fillna('', inplace=True)

    return df

def get_all_files(p):
    filelist = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    return filelist

mypath = "D:\\PROJEKTE\\02_Halbauer\\DyNaMo\\Figurdateien-original"
outfolder = "D:\\PROJEKTE\\02_Halbauer\\DyNaMo\\Figurdateien-kopiert"

df = make_dataframe_from_files(get_all_files(mypath))
#
# # print(df.head())
# df.to_excel("overview_files.xlsx",
#             sheet_name='Überblick')

for idx, fname in zip(df.index, df['orig']):
    src = join(mypath, fname)
    dest = join(outfolder, str(df['name'][idx]) + '.bxy')

    copyfile(src, dest)

