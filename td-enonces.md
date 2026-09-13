# TD - Découvrir Python et préparer son environnement

**UE 0 - Algo 3 avec Python · Chapitre 1**
Marcu-Andria Battesti · Bachelor CLIC · 2026-2027

**Travail individuel.** Chaque étudiant réalise les manipulations dans son
propre dossier et conserve ses fichiers.

À la fin de ces trois TD, vous saurez **lancer un fichier Python, ajouter
un paquet à un projet et reprendre ce projet**.

Avant de commencer, suivez la partie **Préparer le dossier de travail** du
[README](README.md). Gardez [le mémo](memo-a4.md) ouvert pendant la séance.
Sous Windows, toutes les commandes ci-dessous se tapent dans **Git Bash**.

**Deux endroits à distinguer :** les commandes des blocs `bash` se tapent
dans le **terminal**, une ligne à la fois. Le code des blocs `python` se
modifie dans un **fichier ouvert dans l'éditeur**. Enregistrez avant de lancer.

---

# TD 1 - Lancer et modifier un premier programme

**Dossier de départ : `travail-python`**, qui contient `manip`.

## Étape 1 - Vérifier que l'outil répond

```bash
uv --version
```

Un numéro de version doit apparaître. Si le terminal indique que la commande
est introuvable, reprenez l'installation du mémo avec l'enseignant.

`uv` est l'outil qui va préparer Python et lancer nos programmes. Il peut
télécharger Python au premier lancement : attendez le retour du terminal.

## Étape 2 - Lancer un fichier

```bash
uv run manip/bonjour.py
```

Vous devez obtenir :

```text
Bonjour Camille
2 + 3 = 5
```

**À retenir :** `uv run` suivi du chemin d'un fichier lance ce fichier.

## Étape 3 - Faire une petite modification

Ouvrez `manip/bonjour.py` dans l'éditeur. Il contient :

```python
prenom = "Camille"
print("Bonjour", prenom)
print("2 + 3 =", 2 + 3)
```

1. Remplacez `Camille` par votre prénom, en gardant les guillemets.
2. Enregistrez le fichier, puis relancez la même commande dans le terminal.
3. Vérifiez que votre prénom apparaît.

`print` affiche un message. Nous reviendrons sur la syntaxe Python dans les
prochains chapitres.

**Point de contrôle :** chacun doit réussir à modifier, enregistrer et relancer
le programme avant de passer au TD 2.

---

# TD 2 - Créer un projet et ajouter un paquet

**Dossier de départ : `travail-python`**, comme à la fin du TD 1.

Un **projet** est un dossier qui rassemble votre code et les fichiers utiles
pour le faire fonctionner. Un **paquet** est du code déjà écrit que vous
pouvez utiliser dans votre programme.

## Étape 1 - Créer le projet

```bash
uv init --no-package algo3
cd algo3
uv run main.py
```

Vous devez voir `Hello from algo3!`. Le premier lancement crée aussi un
dossier `.venv` : il contient l'environnement Python du projet et accueillera
ses paquets. `uv` s'en occupe automatiquement.

Ouvrez `algo3/main.py` dans l'éditeur. Remplacez **tout son contenu** par :

```python
print("Mon projet fonctionne !")
```

Enregistrez et relancez `uv run main.py`. Vérifiez que le message a changé.

## Étape 2 - Ajouter un paquet

Nous allons utiliser `requests`, un paquet qui permet à Python d'interroger
un site web. Cette étape nécessite une connexion Internet.

```bash
uv add requests
cp ../manip/version_pypi.py .
uv run version_pypi.py requests
```

La commande `cp` copie le programme fourni dans le dossier actuel.
`..` désigne le dossier parent ; le point final `.` désigne le dossier actuel.

Le programme consulte PyPI, le catalogue des paquets Python. Il affiche cinq
lignes : la première nomme `requests` et la dernière indique la version de
`requests` utilisée. **Les numéros peuvent différer entre les postes.**

1. Repérez ces deux lignes. Si elles apparaissent, le programme fonctionne.
2. Consultez maintenant la fiche du paquet `rich` :

```bash
uv run version_pypi.py rich
```

La première ligne doit maintenant nommer `rich`. Le programme utilise toujours
`requests` pour consulter cette fiche.

**Point de contrôle :** vous savez lancer votre code avec `uv run` et ajouter
un paquet avec `uv add`.

---

# TD 3 - Retrouver un projet qui fonctionne

**Dossier de départ : `travail-python/algo3`**, comme à la fin du TD 2.

## Étape 1 - Repérer les fichiers à garder

Ouvrez `algo3/pyproject.toml` dans l'éditeur et repérez la ligne contenant `requests`.
Il suffit de comprendre le rôle de ces fichiers :

| Élément | À quoi sert-il ? |
| --- | --- |
| Les fichiers `.py` | Votre programme |
| `.python-version` | La version de Python demandée |
| `pyproject.toml` | Les paquets demandés par le projet |
| `uv.lock` | Les versions des paquets retenues par uv |
| `.venv` | L'environnement que uv prépare pour ce projet |

Gardez les fichiers du projet. **Il est inutile de partager `.venv` : uv peut
le recréer.** Vous n'avez pas à modifier `uv.lock` à la main.

## Étape 2 - Vérifier sur une copie sans environnement

Nous allons copier le projet dans `algo3-copie`, sans son dossier `.venv`.
Exécutez ces commandes une seule fois depuis `algo3` :

```bash
mkdir ../algo3-copie
cp .python-version pyproject.toml uv.lock README.md main.py version_pypi.py ../algo3-copie/
cd ../algo3-copie
uv sync
uv run version_pypi.py requests
```

`uv sync` prépare l'environnement à partir des fichiers du projet. Vous devez
retrouver les cinq lignes du programme, avec la même version de `requests`
utilisée qu'au TD 2. Le projet d'origine est toujours dans `algo3`.

1. Le programme fonctionne-t-il dans la copie ?
2. Quel dossier uv a-t-il recréé ? Vérifiez avec `ls -a`.

## Étape 3 - Préparer la prochaine séance

Dans le fichier `algo3/README.md`, notez :

```text
Mon projet Python
Ouvrir un terminal dans le dossier algo3, puis exécuter :
uv sync
uv run version_pypi.py requests
```

Pour reprendre le projet une prochaine fois, ouvrez le dossier `algo3` dans
l'éditeur et un terminal dans ce dossier, puis suivez ces instructions.

**Vous avez terminé le parcours principal.** À l'aide du mémo, chacun doit
pouvoir montrer comment lancer un fichier, ajouter un paquet et préparer
l'environnement d'un projet récupéré.

Les [bonus](td-bonus.md) sont facultatifs. L'enseignant peut en montrer un
si cela aide à répondre à une question ; ils ne sont pas nécessaires pour
réussir le parcours principal.
