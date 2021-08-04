import numpy as np
import statistics
from os import path
import math

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


def make_string(n, figType):
    # Daten erzeugen
    array = get_xy(n, figType)

    if figType == 'point':
        ziplist = list(zip(array[0].astype(str), array[1].astype(str)))
        body = [' '.join(x) for x in ziplist]
        head = None
        foot = None
        retString = '\n'.join([*body])
    else:
        head = '# Vector\n# Float\nDATA'
        foot = 'EOF'

        string = ['ABS'] * n
        ziplist = list(zip(string, array[0].astype(str), array[1].astype(str)))
        body = [' '.join(x) for x in ziplist]
        retString = '\n'.join([head, *body, foot])
    return retString


def get_size_of_fig(s):
    return len(s)


def get_quick_sized_string(targetsize, figtype, mode='med', verbose=False):
    if figtype == 'vek':
        strings = {
            'min'  : 'ABS 0 0\n',                      # 8 byte
            'small': 'ABS 0.1 0.1\n',                # 12 byte
            'med'  : 'ABS 0.001 0.001\n',            # 16 byte
            'big'  : 'ABS 0.00001 0.00001\n',        # 20 byte
            'max'  : 'ABS -0.000001 -0.000001\n'     # 24 byte
        }
        head = '# Vector\n'
        foot = 'END\nEOF\n'
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

    len_list = [len(x) for x in strings.values()]

    if rest < min(len_list):
        return full_anz

    for i in reversed(len_list):
        if i > rest:
            continue
        elif i == rest:
            index = i
            anz = 1
        else:
            add = math.floor(rest / i)
            rest = rest % i
    # TODO: Den String in der Liste suchen und zu dem schon gefundenen addieren
    # TODO: Strings verbinden und ausgeben

    return full_anz


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
        elif d_min_glob < -thresh and d_min > -thresh:
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


def create_figure(figType, genMode, outfolder, size=1, points=1, fignr=0, verbose=False):
    if genMode == 'number':
        data = make_string(points, figType)
        size_or_number = f'{points}-pkt_{len(data)}-B'
    elif genMode == 'size':
        data = get_correct_sized_string_loop(size, figType, maxwdh=100, thresh=10, verbose=verbose)
        points = len(data.split("\n"))
        size_or_number = f'{len(data)}-B_{points}-pkt'
    else:
        raise ValueError

    if fignr > 0:
        nr = f'_{fignr}'
    else:
        nr = ''

    outfile = f'{figType}-Fig_{size_or_number}{nr}.bxy'
    out = path.join(outfolder, outfile)
    with open(out, 'w') as f:
        f.write(data)


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


if __name__ == "__main__":
    outfolder = 'data'

    # figures_per_size = 10

    # 'point' oder 'vek' mgl.
    figType = 'vek'

    # 'number' oder 'size' möglich
    genMode = 'size'
    # Faktoren für KB
    faks = [#1, 2, 3, 4, 5, 6, 7,8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000,
             2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000,
            10000, 100000, 200000]
    # faks = [1]
    size = [x*1024 for x in faks]

    pointcount = [x * 10 for x in faks]


    # testfunktion, um einen Eindruck über die Startwerte für N zu erhalten
    # get_good_start_vals(nlist, wdh, figType)

    # for s, f in zip(size, faks):
    #     print(f'Faktor: {f}, Size:{s}')

    #     create_figure(figType, genMode, outfolder, size=s, points=pointcount, verbose=True)

    print(get_quick_sized_string(size[0], figType))

    # testfile = 'data/point-Fig_1024-B.bxy'
    #
    # print(get_size_of_file(testfile))





