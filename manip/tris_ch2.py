# Les tris du chapitre 2, avec leur compteur de comparaisons - au cas où les
# vôtres se seraient perdus. Chaque fonction renvoie (liste triée, comparaisons).
#
#   from tris_ch2 import tri_selection, tri_insertion, tri_fusion


def tri_selection(t):
    t = list(t)
    comparaisons = 0
    n = len(t)
    for i in range(n - 1):
        mini = i
        for j in range(i + 1, n):
            comparaisons += 1
            if t[j] < t[mini]:
                mini = j
        t[i], t[mini] = t[mini], t[i]
    return t, comparaisons


def tri_insertion(t):
    t = list(t)
    comparaisons = 0
    for i in range(1, len(t)):
        x = t[i]
        j = i - 1
        while j >= 0:
            comparaisons += 1
            if t[j] > x:
                t[j + 1] = t[j]
                j -= 1
            else:
                break
        t[j + 1] = x
    return t, comparaisons


def fusion(g, d, cpt):
    resultat = []
    i = j = 0
    while i < len(g) and j < len(d):
        cpt[0] += 1
        if g[i] <= d[j]:
            resultat.append(g[i])
            i += 1
        else:
            resultat.append(d[j])
            j += 1
    resultat.extend(g[i:])
    resultat.extend(d[j:])
    return resultat


def _tri_fusion(t, cpt):
    if len(t) <= 1:
        return list(t)
    m = len(t) // 2
    return fusion(_tri_fusion(t[:m], cpt), _tri_fusion(t[m:], cpt), cpt)


def tri_fusion(t):
    cpt = [0]
    return _tri_fusion(t, cpt), cpt[0]
