# TD - Découvrir Python et préparer son environnement

**UE 0 - Algo 3 avec Python · Chapitre 1**
Marcu-Andria Battesti · Bachelor CLIC · 2026-2027


> Prérequis : **uv** installé (`uv --version` répond), git, un terminal.
> Sous Windows : **Git Bash**. Les commandes `uv` sont les mêmes partout ;
> seules changent `py` à la place de `python3`, `where` à la place de
> `which -a`, et `Scripts` à la place de `bin` dans les chemins.
>
> Le dossier `manip/` du chapitre se copie une fois dans un dossier de
> travail. Tout ce que les TD créent (`algo3/`, `vieux-projet/`,
> `tableau-de-bord/`) naît à côté de lui, dans ce même dossier.

---

# TD 1 - Quel Python ?

## Étape 0 - L'outil et les Python du poste 

```bash
uv --version
uv python list --only-installed
which -a python3                  # Windows : where python
```

1. La version d'uv. Combien de Python `uv` connaît-il sur ce poste ?
2. Combien de lignes renvoie `which -a` ? Sont-ce les mêmes chemins ?

## Étape 1 - Celui qu'uv choisit 

```bash
uv python find
uv run python
```

Dans le REPL qui s'ouvre :

```python
import sys
sys.version
sys.executable
exit()
```

1. Comparez `sys.executable` à la réponse de `uv python find`.
2. Recommencez avec `python3` tout court (Windows : `py`). Même
   exécutable ?

## Étape 2 - Un script

Lisez `manip/quel_python.py`, puis :

```bash
uv run manip/quel_python.py
python3 manip/quel_python.py      # Windows : py manip/quel_python.py
```

1. Repérez les quatre lignes ; notez seulement l'exécutable et « dans un venv ».
2. La ligne « dans un venv » compare deux valeurs : lesquelles, et
   pourquoi `False` ?
3. ★ Le même fichier lancé par deux Python différents peut donner deux
   résultats. Qu'est-ce que cela dit du rapport entre un fichier `.py` et
   « le programme » ?

## Étape 3 - Un autre Python, sans rien casser

```bash
uv run --python 3.13 manip/quel_python.py
uv python list --only-installed
```

Sans réseau : l'enseignant le montre au projecteur.

1. Quelles lignes ont changé par rapport à l'étape 2 ?
2. Où ce Python a-t-il été rangé ? Le poste en a-t-il un de plus ou de
   moins qu'au début ?
3. ★ Que garantit `uv run` que `python3` ne garantit pas ?

---

# TD 2 - Deux ateliers

**40 minutes · en binôme · sur machine**

## Étape 0 - Naissance d'un projet

```bash
uv init algo3
cd algo3
ls -a
cat pyproject.toml
cat .python-version
```

1. Les fichiers créés. Lequel dit quel Python le projet veut ?
2. `dependencies = []` : que promet cette ligne pour l'instant ?

## Étape 1 - Le premier `run`

```bash
uv run main.py
ls -a
ls .venv                          # Windows : ls .venv/Scripts
cat .venv/pyvenv.cfg
uv run ../manip/quel_python.py
```

1. Deux choses sont apparues dans le dossier : lesquelles ?
2. La ligne `home =` : que désigne-t-elle ?
3. Quelles lignes de `quel_python.py` ont changé depuis le TD 1 ?

## Étape 2 - Activer, ou pas

```bash
echo $PATH | cut -d: -f1
source .venv/bin/activate         # Windows : source .venv/Scripts/activate
echo $PATH | cut -d: -f1
which python
python ../manip/quel_python.py
deactivate
.venv/bin/python ../manip/quel_python.py     # Windows : .venv/Scripts/python
```

1. Ce qui a changé dans le PATH, et dans l'invite.
2. ★ Trois façons de lancer le script ont donné le même résultat.
   Qu'est-ce que l'activation, exactement, et pourquoi `uv run` s'en
   passe-t-il ?

## Étape 3 - Deux versions

```bash
uv add requests
cat pyproject.toml
uv tree
uv pip show requests
```

1. Combien de paquets installés pour un seul demandé ?
2. La ligne ajoutée à `pyproject.toml` : est-ce un numéro exact ?
3. `Location` : où vivent ces paquets ?

```bash
cp ../manip/version_pypi.py .
uv run version_pypi.py requests
```

Un second projet, avec une vieille version :

```bash
cd ..
uv init vieux-projet
cd vieux-projet
uv add "requests==2.25.1"
uv tree
```

4. Un nom diffère entre les deux arbres : lequel ? Qu'est-ce que
   « mettre à jour requests » entraîne ?
5. **Bonus après la séance** : `uv run ../algo3/version_pypi.py requests`
   ici. Une ligne diffère de la sortie dans `algo3` : laquelle, pourquoi ?

## Étape 4 - Hors de l'atelier

```bash
cd ..
python3 -c "import requests"      # Windows : py -c "import requests"
```

1. Que répond Python ? Si ça marche, trouvez quel Python répond et où vit
   ce `requests`.
2. ★ Le binôme envoie un script qui commence par `import requests` :
   « ça marche sur ma machine ». Pourquoi pas sur la vôtre, et qu'est-ce
   qui aurait dû voyager avec le script ?

> Ne supprimez pas `algo3`. `vieux-projet` a fini son travail.

---

# TD 3 - Reproduire

**40 minutes · en binôme · dont 5 minutes de démonstration**

Dans `algo3`.

## Étape 1 - Ce qu'un paquet apporte, ce qu'il emporte *(5 min, démo enseignant)*

Gardez votre projet intact. Avant chaque commande au projecteur,
prédisez le résultat puis répondez sur la fiche.

```bash
uv tree
uv remove requests
uv pip list
cat pyproject.toml
```

1. Combien de paquets retirés pour un seul nom ?
2. Qu'a fait `uv remove` que `pip uninstall requests` n'aurait pas fait ?
3. Qu'est-ce qui a changé dans `pyproject.toml` ? Et dans `uv.lock` ?

L'enseignant remet `requests`. Les binômes passent à l'étape 2 avec le
paquet toujours présent dans leur propre projet.

## Étape 2 - Deux fichiers pour un contrat

```bash
cat pyproject.toml
grep '^name = \|^version = ' uv.lock
```

1. `pyproject.toml` dit `requests>=2.34.2` ; `uv.lock` dit `2.34.2`, et
   quatre autres numéros. Lequel des deux fichiers est l'intention,
   lequel est la photo ?
2. ★ Pourquoi partager les deux ? Le scénario où `pyproject.toml` seul
   trahit le binôme.

Détruisez, puis reconstruisez :

```bash
rm -rf .venv
uv sync
uv pip list
uv run version_pypi.py requests
python3 -c "import requests"      # Windows : py -c "import requests"
```

3. La liste est-elle identique ? Qu'a lu `uv sync` pour la refaire ?
4. Que répond la dernière commande, et pourquoi est-ce rassurant ?

## Étape 3 - Le contrat qui ment ★

```bash
cd ..
cp -r manip/tableau-de-bord .
cd tableau-de-bord
cat pyproject.toml
uv sync
```

1. ★ Lisez l'erreur avant de toucher au fichier. Recopiez la phrase qui
   commence par `Because`. Quelle cause ? À quoi le voyez-vous ?
2. Corrigez cette ligne seulement, relancez. Nouvelle erreur : même question.
   Pour trouver un numéro qui existe : `version_pypi.py` depuis `algo3`,
   ou retirer l'épingle et lire ce qu'uv a choisi.
3. Corrigez, relancez. Puis `uv run tableau.py` et `uv tree`. Combien de
   paquets pour deux lignes de contrat ?

## Étape 4 - Prêt à cloner

De retour dans `algo3` :

```bash
cat .gitignore
git status
```

1. `.venv/` apparaît-il ? Qui a écrit `.gitignore` ? Quels fichiers git
   propose-t-il de suivre ?
2. Remplacez `README.md` par quatre lignes : le nom du projet, les deux
   commandes pour le reconstruire et lancer `version_pypi.py`.
   **Prolongement après la séance** : `git add .` et un premier commit.
3. ★ Le binôme clone ce dépôt sur un poste neuf où seul uv est installé,
   sans Python. Les commandes exactes, dans l'ordre, pour lancer
   `version_pypi.py`. Pas une de plus. D'où vient le Python ?

> Le mémo `memo-a4.md`, distribué en fin de séance, reprend toutes les
> commandes.
