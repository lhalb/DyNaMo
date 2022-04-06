import os, fnmatch
import re
import pandas as pd

if __name__ == "__main__":
    # Wo liegen die .MPF Logfiles
    src = r"C:\Users\halbauer\Desktop\logs"

    # Wo soll die Ergebnisdatei gespeichert werden
    dest = r"C:\Users\halbauer\Desktop\logs"

    # Ausgabename der vollständigen Exceldatei
    fname = 'results.xlsx'

    # Liste, in der Bezeichnung der Figuren enthalten ist
    datalist = r"C:\Users\halbauer\Desktop\overview_files.xlsx"

    # dictionary mit Spalten und Namen der auszuwertenden Kenngrößen
    to_calc = {
        'ram': 'figload',
        'wrt': 'wrt',
        'pc-1': 'pc_read_1',
        'pc-2': 'pc_read_2'
    }

    # Name der Spalten
    names = ['nr', 'wdh', 'slot'] + list(to_calc.keys())

    # Dateien aus dem Quellverzeichnis auflisten
    files = fnmatch.filter(os.listdir(src), '*.MPF')

    # als Dataframe einlesen
    df_list = [pd.read_table(os.path.join(src, file), comment='#', sep=' ', header=None, names=names)
               for file in files]

    # zu einem Dataframe zusammenfügen
    big_df = pd.concat(df_list)

    # Gruppiere die Daten nach Nr und bilde von WRT und RAM
    # den Median
    medians = big_df.groupby('nr')[list(to_calc.keys())].median()
    # das Maximum
    # maxs = big_df.groupby('nr')[['ram', 'wrt']].max()
    # Das Minimum
    # mins = big_df.groupby('nr')[['ram', 'wrt']].min()

    # benenne entsprechend
    medians = medians.rename(columns=to_calc)
    # maxs = maxs.rename(columns={'ram': 'ram-max', 'wrt': 'wrt-max'})
    # mins = mins.rename(columns={'ram': 'ram-min', 'wrt': 'wrt-min'})

    medians['sum-med'] = medians[[to_calc['ram'], to_calc['wrt']]].sum(axis=1)

    ergs = medians
    # ergs = pd.concat([medians, maxs, mins], axis=1)

    df = pd.read_excel(datalist, index_col=2)

    try:
        combined_df = pd.concat([df, ergs], axis=1)
    except pd.errors.InvalidIndexError:
        df['ft'] = df.index
        df.index = list(range(1, len(df)+1))
        combined_df = pd.concat([df, ergs], axis=1)

    combined_df.to_excel(os.path.join(dest, fname))
