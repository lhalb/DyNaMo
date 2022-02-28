from tqdm import tqdm
import numpy as np
import statistics
from os import path
import math
from time import time, sleep


def get_xy(n, figType):
    x_numbers = np.random.randint(0, 65535+1, n)
    y_numbers = np.random.randint(0, 65535+1, n)

    if figType == 'point':
        x = x_numbers
        y = y_numbers
    else:
        x = (x_numbers - 32767.5) / 32767.5
        x = x.astype(np.float16)
        y = (y_numbers - 32767.5) / 32767.5
        y = y.astype(np.float16)
    return np.vstack((x, y))


def get_vector_head():
    return '# Vector\nDATA\n'

def get_vector_foot():
    return 'END\nEOF'


def make_string(n, figType):
    """
    Function to generate coordinates for mode 'number'.

    :param n: number of coordinates
    :param figType: point or vector figure
    :return: strings for coordinates
    """
    n = int(n)
    # Daten erzeugen
    array = get_xy(n, figType)

    if figType == 'point':
        ziplist = list(zip(array[0].astype(str), array[1].astype(str)))
        body = [' '.join(x) for x in ziplist]
        head = None
        foot = None
        return_string = '\n'.join([*body])
    else:
        head = get_vector_head()
        foot = get_vector_foot()
        if figType == 'vek':
            string = ['ABS'] * n
            ziplist = list(zip(string, array[0].astype(str), array[1].astype(str)))
            body = [' '.join(x) for x in ziplist]
        else:   # if type == 'vek-small'
            body = [f'ABS -1 -1\nREL 1 1 {n}']

        return_string = '\n'.join([head, *body, foot])
    return return_string


def get_size_of_fig(s):
    return len(s)


def get_quick_sized_string(targetsize, figtype, mode='med', comment=None, verbose=False):
    if figtype == 'vek':
        strings = {
            'min': 'ABS 0 0\n',                      # 8 byte
            'small': 'ABS 0.1 0.1\n',                # 12 byte
            'med': 'ABS 0.001 0.001\n',            # 16 byte
            'big': 'ABS 0.00001 0.00001\n',        # 20 byte
            'max': 'ABS -0.000001 -0.000001\n'     # 24 byte
        }
        head = get_vector_head()
        foot = get_vector_foot()
    elif figtype == 'point':
        strings = {
            'min': '0 0\n',              # 4 byte
            'small': '10 10\n',          # 6 byte
            'med': '100 100\n',          # 8 byte
            'big': '1000 1000\n',        # 10 byte
            'max': '10000 10000\n'       # 12 byte
        }
        head = ''
        foot = ''
    else:
        print('Falschen Figurtyp angegeben')
        return False

    static_len = len(head + foot)
    full_anz = math.floor((targetsize-static_len)/len(strings[mode]))
    rest = (targetsize-static_len) % len(strings[mode])

    body = strings[mode]*full_anz

    len_list = [len(x) for x in strings.values()]

    if rest < min(len_list):
        pass
    else:
        for i in reversed(len_list):
            if i > rest:
                continue
            elif i == rest:
                idx_elem = len_list.index(i)
                body += list(strings.values())[idx_elem]
                full_anz += 1
                break
            else:
                anz = math.floor(rest / i)
                idx_elem = len_list.index(i)
                body += anz * list(strings.values())[idx_elem]
                full_anz += anz
                rest = rest % i

    if verbose:
        print(f'Figur erfolgreich erzeugt\nGenauigkeit: {rest}, Punkte: {full_anz}')

    return head + body + foot, full_anz


def get_correct_sized_string_loop(targetsize, figtype, maxwdh, thresh=10, verbose=False):
    def get_minimum_string(ts, sl, min_diff):
        ll = list(map(len, sl))
        dl = [x - ts for x in ll]
        # speichere den Index des aktuellen Minimums
        min_idx = dl.index(min_diff)
        # suche diesen Index in der Stringliste
        ret_val = sl[min_idx]
        return ret_val

    def create_stringlist(n, figtype, matsize):
        return [make_string(n, figtype) for i in range(matsize)]

    def get_dmin(ts, sl):
        lenlist = list(map(len, sl))

        sd = [x - ts for x in lenlist]

        return min(sd)

    if figType == 'point':
        # diesen Faktor einstellen, wenn die Routine ewig keine Ergebnisse liefert
        fak = 12

    if figType == 'vek':
        fak = 20

    if targetsize < 1e5:
        matsize = 50
    elif targetsize < 1e6:
        matsize = 25
    elif targetsize < 1e7:
        matsize = 15
    else:
        matsize = 10

    nlist = []
    n = int(targetsize / fak)

    stringlist = create_stringlist(n, figtype, matsize)
    d_min = get_dmin(targetsize, stringlist)

    d_min_glob = d_min

    minstring = get_minimum_string(targetsize, stringlist, d_min_glob)

    trys = 0
    fak_exp = math.floor(math.log10(targetsize)) - 1
    n_fak = int(1*10**fak_exp)
    while d_min_glob != 0:
        if verbose:
            print(f'{n}, {d_min}, {d_min_glob}, {trys}')

        if trys > maxwdh:
            break
        if d_min_glob < -thresh and d_min < -thresh:
            n += 1*n_fak
            nlist.append(n)
        elif d_min_glob > thresh and d_min < -thresh:
            n += 1 * n_fak
            nlist.append(n)
        elif d_min_glob < -thresh < d_min:
            n -= 1*n_fak
            if n_fak > 1:
                n_fak = int(n_fak*0.1)
            nlist.append(n)
        elif d_min_glob > thresh and d_min > thresh:
            n -= 1*n_fak
            if n_fak > 1:
                n_fak = int(n_fak*0.1)
            nlist.append(n)
        else:
            trys += 1
        stringlist = create_stringlist(n, figtype, matsize)
        d_min = get_dmin(targetsize, stringlist)
        if d_min == 0:
            minstring = get_minimum_string(targetsize, stringlist, d_min)
        if abs(d_min) < abs(d_min_glob):
            d_min_glob = d_min
            minstring = get_minimum_string(targetsize, stringlist, d_min_glob)

    return minstring


def create_figure(figType, figure_mode, savefolder, size_mode='rough',
                  size=1, points=1, fignr=0, bytesize='med', verbose=False):
    if figure_mode == 'number':
        data = make_string(points, figType)
        size_or_number = f'{points}-pkt_{len(data)}-B'
    elif figure_mode == 'size':
        if size_mode == 'rough':
            data, points = get_quick_sized_string(size, figType, bytesize)
            size_or_number = f'{len(data)}-B_{bytesize}_{points}-pkt'
        elif size_mode == 'precise':
            data = get_correct_sized_string_loop(size, figType, maxwdh=100, thresh=10, verbose=verbose)
            points = len(data.split("\n"))
            size_or_number = f'{len(data)}-B_{points}-pkt'
        else:
            raise ValueError(f'Der Berechnungsmodus >{size_mode}< ist nicht bekannt.')
    else:
        raise ValueError(f'Der Figurtyp >{figure_mode}< ist nicht bekannt')

    if fignr > 0:
        nr = f'_{fignr}'
    else:
        nr = ''

    ext = get_extension(figType)

    outfile = f'{figType}-Fig_{figure_mode}_{size_or_number}{nr}{ext}'
    out = path.join(savefolder, outfile)
    with open(out, 'w') as f:
        f.write(data)


def get_extension(ft):
    if ft == 'point':
        e = '.bxy'
    elif 'vek' in ft:
        e = '.bvc'
    else:
        raise ValueError('Figurtyp unbekannt')
    return e


def get_size_of_file(fname):
    with open(fname, "r") as f:
        data = f.read()

    lines = len(data.split("\n"))

    return len(data), lines


def get_good_start_vals(nlist, wdh, figType):
    lenlist = [[len(make_string(n, figType)) for i in range(wdh)] for n in nlist]

    abw = list(map(statistics.stdev, lenlist))
    print('Liste mit Längen der geschriebenen Figuren:\n', lenlist)
    print('Wie groß sind die Abweichungen vom Durchschnitt?\n', abw)

    fak_list = [0] * len(nlist)
    for i in range(len(nlist)):
        fak_list[i] = statistics.mean(lenlist[i])/nlist[i]

    print('Mit welchem Faktor kann man n multiplizieren, um auf den Durchschnitt zu kommen?\n', fak_list)


def calc_figures(figtypes, calctypes, factors, modes=None):
    all_figures = 0
    if len(figtypes) == 0:
        raise AttributeError('Too less figtypes!')

    if 'number' in calctypes:
        all_figures += len(factors) * len(figtypes)
    if 'size' in calctypes:
        if len(modes) == 0:
            raise AttributeError('Too less size modes!')

        all_figures += len(factors) * len(figtypes) * len(modes)

    return all_figures


def loop_parameters(FT, GM, CM, PC=None, S=None, F=None, BS=None, verb=False):
    fig_count = calc_figures(FT, GM, F, CM)
    if verb:
        print(f'Anzahl Figuren: {fig_count}')
    with tqdm(total=fig_count) as pbar:
        for ft in FT:
            for gm in GM:
                if gm == 'size':
                    if CM == 'rough':
                        for bs in BS:
                            for s, f in zip(S, F):
                                t1 = time()
                                create_figure(ft, gm, outfolder, size=s, size_mode=CM, bytesize=bs, verbose=verb)
                                t2 = time()
                                pbar.update(1)
                                sleep(0.25)
                                if verb:
                                    print(f'Faktor: {f}, Groesse: {s}\nZeit zur Bearbeitung {t2 - t1}s \n')
                    else:
                        for s, f in zip(S, F):
                            t1 = time()
                            create_figure(ft, gm, outfolder, size=s, size_mode=CM, verbose=verb)
                            t2 = time()
                            pbar.update(1)
                            sleep(0.25)
                            if verb:
                                print(f'Faktor: {f}, Groesse: {s}\nZeit zur Bearbeitung {t2 - t1}s \n')

                if gm == 'number':
                    for p, f in zip(PC, F):
                        t1 = time()
                        create_figure(ft, gm, outfolder, points=p, verbose=verb)
                        t2 = time()
                        pbar.update(1)
                        sleep(0.25)
                        if verb:
                            print(f'Faktor: {f}, Punkte: {p}\nZeit zur Bearbeitung {t2 - t1}s \n')


if __name__ == "__main__":
    outfolder = 'F:\\Figs_dyn_points'

    # figures_per_size = 10

    # 'point', 'vek' oder 'vek-small' mgl.
    figType = ['vek', 'point', 'vek-small']

    # min, small, med, big, max mgl.
    bytesize = ['min', 'small', 'big', 'med', 'max']

    # 'number' oder 'size' möglich
    genMode = ['number']

    # 'rough' oder 'precise' mgl.
    # --> 'precise' benötigt tw. immense Speichermengen und ist extrem langsam bei großen Dateien
    # --> sollte nur bei Dateien bis 100 KB eingesetzt werden
    calc_mode = 'rough'

    v = False

    # Faktoren für KB
    # faks = [1, 1000, 1e5]
    # faks = [1, 2, 3, 4, 5, 6, 7, 8, 9,
    #         10, 20, 30, 40, 50, 60, 70, 80, 90,
    #         100, 200, 300, 400, 500, 600, 700, 800, 900,
    #         1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000,
    #         1e4, 2e4, 3e4, 4e4, 5e4, 6e4, 7e4, 8e4, 9e4,
    #         1e5, 2e5, ]
    faks = [i*10**j for j in range(9) for i in range(1, 10)]

    # -----------------------------------------------------------------------------------------------------------------
    # ---------------------------------------- Ab hier beginnt eigentliches Programm ----------------------------------
    # -----------------------------------------------------------------------------------------------------------------

    size = [int(x*1000) for x in faks]
    pointcount = [int(x * 10) for x in faks]

    # testfunktion, um einen Eindruck über die Startwerte für N zu erhalten
    # get_good_start_vals(nlist, wdh, figType)

    # Funktion, um alle Parameter durchzutesten
    loop_parameters(FT=figType, GM=genMode, CM=calc_mode, PC=pointcount, S=size, F=faks, BS=bytesize, verb=v)

    # testfile = 'data/vek-Fig_size_99999993-B_min_12499997-pkt.bxy'
    #
    # print(get_size_of_file(testfile))





