from tqdm import tqdm
from shutil import copyfile
import pandas as pd
from os import listdir
from os.path import isfile, join
from time import sleep


def make_dataframe_from_files(files, size_sort=False):
    df = pd.DataFrame({'orig': files})

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

    df['ext'] = [s.split('.')[1] for s in df['orig']]

    if size_sort:
        df['f-size'] = pd.to_numeric(df['f-size'])
        df = df.sort_values(by=['f-size'])

    # erstelle namensspalte
    df['name'] = range(1, len(df['orig']) + 1)

    return df


def get_all_files(p):
    filelist = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    return filelist


if __name__ == '__main__':
    mypath = "D:\\figs_neu"
    outfolder = "D:\\figs_copy"

    sort_by_size = True

    data_log = make_dataframe_from_files(get_all_files(mypath), sort_by_size)
    #
    # # print(df.head())
    data_log.to_excel(join(outfolder, "overview_files.xlsx"),
                      sheet_name='Überblick')

    with tqdm(total=len(data_log['orig'])) as pbar:
        for idx, fname in zip(data_log.index, data_log['orig']):
            src = join(mypath, fname)
            dest = join(outfolder, str(data_log['name'][idx]) + '.' + data_log['ext'][idx])

            copyfile(src, dest)
            pbar.update(1)
            sleep(0.25)
