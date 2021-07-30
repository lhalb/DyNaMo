import numpy as np
import statistics
from os import path

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
        head = 'DATA'
        foot = 'EOF'

        string = ['ABS'] * n
        ziplist = list(zip(string, array[0].astype(str), array[1].astype(str)))
        body = [' '.join(x) for x in ziplist]
        retString = '\n'.join([head, *body, foot])
    return retString

def get_size_of_fig(s):
    return len(s)


def get_correct_sized_string(targetSize, figType, wdh=10, matSize=100, thresh=10, n=None, nlist=[], mindiff=None, minstring=None, test=0, status=False):
    """
    Startwerte für Faktor size = fak*n (empirisch ermittelt):
        Vektorfiguren
            n < 10: fak < 30
            n >=10: 18< fak < 20
            n > 100: fak < 18.5
        Punktfiguren
            n >= 1: fak < 10
    :param targetSize: Größe, die Die Figur haben soll
    :param wdh: wie oft soll getestet werden, bis Optimum erreicht ist?
    :param matSize: wie viele Möglichkeiten sollen gleichzeitig getestet werden? --> erhöht Speicherbedarf
    :param thresh: auf wie viele Bytes genau soll die Figur gefunden werden?
    :return: Figurstring
    """
    def get_minimum_string(dl, sl, min_diff):
        # speichere den Index des aktuellen Minimums
        min_idx = dl.index(min_diff)
        # suche diesen Index in der Stringliste
        ret_val = sl[min_idx]
        return ret_val

    if figType == 'point':
        # diesen Faktor einstellen, wenn die Routine ewig keine Ergebnisse liefert
        fak = 9

    if figType == 'vek':
        fak = 15

    if not n:
        n = int(targetSize / fak)
        nlist.append(n)

    stringlist = [make_string(n, figType) for i in range(matSize)]

    lenlist = list(map(len, stringlist))

    # print(lenlist)
    sd = [x - targetSize for x in lenlist]

    # print(sd)

    min_it, max_it = min(sd), max(sd)

    # print(min_it, max_it)
    # print(nlist)

    # wenn die kleinste Differenz zu groß ist
    if min_it > thresh:
        n -= 1
    elif max_it < thresh:
        n += 1
        # wenn diese Anzahl an Punkten noch nicht getestet wurde
    elif min_it == 0:
        return get_minimum_string(sd, stringlist, min_it)

    if n not in nlist:
        nlist.append(n)
        return get_correct_sized_string(targetSize, figType, wdh=wdh, matSize=matSize, thresh=thresh, n=n, nlist=nlist)
    else:
        # zähle die Testvariable 1 hoch
        test += 1

        if test <= wdh:
            if not mindiff or abs(min_it) < mindiff:
                ms = get_minimum_string(sd, stringlist, min_it)
                return get_correct_sized_string(targetSize, figType, wdh=wdh, matSize=matSize, thresh=thresh, n=n, test=test,
                                         mindiff=min_it, minstring=ms, nlist=nlist)
            else:
                ms = minstring
                return get_correct_sized_string(targetSize, figType, wdh=wdh, matSize=matSize, thresh=thresh, n=n, test=test,
                                         mindiff=mindiff, minstring=ms, nlist=nlist)

        else:
            return minstring


def create_figure(figType, genMode, outfolder, size=1, points=1, fignr=0):
    if genMode == 'number':
        data = make_string(points, figType)
        size_or_number = f'{points}-pkt'
    elif genMode == 'size':
        data = get_correct_sized_string(size, figType, wdh=10, matSize=100, thresh=10)
        size_or_number = f'{size}-B'
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
    with open(fname) as f:
        data = f.read()

    return len(data)


def get_good_start_vals(nlist, wdh, figType):
    lenlist = [[len(make_string(n, figType)) for i in range(wdh)] for n in nlist]

    abw = list(map(statistics.stdev, lenlist))
    print('Liste mit Längen der geschriebenen Figuren:\n', lenlist)
    print('Wie groß sind die Abweichungen vom Durchschnitt?\n', abw)

    fak_list = [0] * len(nlist)
    for i in range(len(nlist)):
        fak_list[i] = statistics.mean(lenlist[i])/nlist[i]

    print('Mit welchem Faktor kann man n multiplizieren, um auf den Durchschnitt zu kommen?\n', fak_list)



outfolder = 'data'

figures_per_size = 10

# 'point' oder 'vek' mgl.
figType = 'point'

# 'number' oder 'size' möglich
genMode = 'size'

size = 1000
pointcount = 2000


# testfunktion, um einen Eindruck über die Startwerte für N zu erhalten
# get_good_start_vals(nlist, wdh, figType)


for i in range(figures_per_size):
    create_figure(figType, genMode, outfolder, size=size, points=pointcount, fignr=i)







