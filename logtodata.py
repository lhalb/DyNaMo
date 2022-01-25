import os
import re
import pandas as pd

if __name__ == "__main__":
    # Wo liegen die .MPF Logfiles
    src = "data/datalogs"

    # Wo soll die Ergebnisdatei gespeichert werden
    dest = "data"

    # Ausgabename der vollständigen Exceldatei
    fname = 'results.xlsx'

    # Liste, in der Bezeichnung der Figuren enthalten ist
    datalist = "overview_files.xlsx"

    # Name der Spalten
    names = ['nr', 'wdh', 'slot', 'ram', 'wrt']

    # Dateien aus dem Quellverzeichnis auflisten
    files = os.listdir(src)

    # als Dataframe einlesen
    df_list = [pd.read_table(os.path.join(src, file), comment='#', sep=' ', header=None, names=names)
               for file in files]

    # zu einem Dataframe zusammenfügen
    big_df = pd.concat(df_list)

    # Gruppiere die Daten nach Nr und bilde von WRT und RAM
    # den Median
    medians = big_df.groupby('nr')[['ram', 'wrt']].median()
    # das Maximum
    maxs = big_df.groupby('nr')[['ram', 'wrt']].max()
    # Das Minimum
    mins = big_df.groupby('nr')[['ram', 'wrt']].min()

    # benenne entsprechend
    medians = medians.rename(columns={'ram': 'ram-med', 'wrt': 'wrt-med'})
    maxs = maxs.rename(columns={'ram': 'ram-max', 'wrt': 'wrt-max'})
    mins = mins.rename(columns={'ram': 'ram-min', 'wrt': 'wrt-min'})

    medians['sum-med'] = medians.sum(axis=1)

    ergs = pd.concat([medians, maxs, mins], axis=1)

    df = pd.read_excel(datalist, index_col=2)

    combined_df = pd.concat([df, ergs], axis=1)

    combined_df.to_excel(os.path.join(dest, fname))
