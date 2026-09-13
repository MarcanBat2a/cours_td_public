# Mémo - Travailler avec Python et uv

**UE 0 - Algo 3 avec Python · Chapitre 1**
À garder ouvert dès le début de la séance et à chaque nouveau projet.

## Installer uv, une fois par poste

| macOS, Linux : dans le terminal | Windows : dans PowerShell |
| --- | --- |
| `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` |

Rouvrez ensuite le terminal et tapez `uv --version` : un numéro doit apparaître.
Pour la suite du TD sous Windows, utilisez **Git Bash**.
uv peut télécharger Python quand il en a besoin.

## Les commandes à retenir

Toutes ces commandes se tapent dans le **terminal**.

| Je veux… | Je tape… |
| --- | --- |
| Créer un projet nommé `algo3` | `uv init --no-package algo3` |
| Entrer dans son dossier | `cd algo3` |
| Lancer un fichier du projet | `uv run main.py` |
| Ajouter un paquet au projet | `uv add requests` |
| Préparer l'environnement d'un projet récupéré | `uv sync` |

Pour les trois dernières commandes, placez-vous dans le dossier du projet.
Modifiez le code dans **l'éditeur**, enregistrez, puis relancez dans le terminal.

## Retrouver son dossier

`pwd` affiche le dossier actuel ; `ls` affiche son contenu (`ls -a` inclut les
fichiers cachés). `cd ..` remonte d'un dossier. `mkdir nom` crée un dossier.
`cp source destination` copie un fichier ; `cp -R` copie un dossier.

## Les fichiers du projet

| À garder et à partager | Rôle |
| --- | --- |
| Vos fichiers `.py` et `README.md` | Le programme et ses instructions |
| `.python-version` | Le Python demandé |
| `pyproject.toml` | Les paquets demandés |
| `uv.lock` | Les versions retenues par uv |

**`.venv` se recrée avec `uv sync`** : inutile de le partager.
Quand les fichiers du projet sont inchangés, uv réutilise les versions
retenues dans `uv.lock`. Laissez uv gérer ce fichier.

## Si quelque chose bloque

- **`uv` introuvable** : rouvrir le terminal ; vérifier l'installation.
- **Fichier introuvable** : regarder `pwd`, puis `ls`, et vérifier le nom du fichier.
- **Le message affiché n'a pas changé** : enregistrer le fichier dans l'éditeur,
  puis relancer la commande.
- **Le terminal affiche `>>>`** : vous êtes dans Python. Taper `exit()` pour
  revenir au terminal, puis saisir la commande `uv run ...`.
- **Problème de réseau** : appeler l'enseignant. Les
  [sorties de secours](manip/sorties-sans-reseau.md) permettent d'observer les
  résultats des manipulations de paquets, puis de les refaire une fois connecté.
