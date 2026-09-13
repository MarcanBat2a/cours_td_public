# Chapitre 1 - Découvrir Python et préparer son environnement

**UE 0 - Algo 3 avec Python** · TD et matériel de séance
Histoire, usages en entreprise, un atelier par projet et ses paquets avec uv

Branche : `tp/ue0-01-environnement-python`

## Récupérer le TD

```bash
git clone https://github.com/MarcanBat2a/cours_td_public.git
cd cours_td_public
git switch tp/ue0-01-environnement-python
```

Si vous avez déjà le dépôt, `git fetch origin` puis `git switch tp/ue0-01-environnement-python`.

## Ce que contient la branche

- `manip/` - les fichiers à utiliser pendant la séance sur machine
- `memo-a4.md` - le mémo à garder ouvert dès le début de la séance,
  matière de la feuille A4 autorisée à l'épreuve
- `td-enonces.md` - l'énoncé des travaux dirigés
- `td-bonus.md` - les approfondissements facultatifs et les démonstrations enseignant

Chaque chapitre a sa branche : `git switch tp/<ue>-<chapitre>`. La branche
`master` en donne la liste.

## Préparer le dossier de travail

Il faut **uv**, **Git** et un éditeur de texte ou de code. Sous Windows,
utilisez **Git Bash** pour les commandes du TD. Si uv manque, son installation
est expliquée dans [le mémo](memo-a4.md). Rouvrez ensuite le terminal et
vérifiez que `uv --version` affiche un numéro de version.

Après les commandes de récupération ci-dessus, vous êtes dans
`cours_td_public`. Exécutez **une seule fois**, une ligne à la fois :

```bash
cd ..
mkdir travail-python
cp -R cours_td_public/manip travail-python/
cd travail-python
pwd
ls
```

`cd` change de dossier, `mkdir` crée un dossier, `cp -R` copie un dossier,
`pwd` affiche où vous êtes et `ls` affiche son contenu.
Le chemin affiché doit finir par `travail-python`, et `ls` doit montrer `manip`.
Si `travail-python` existe déjà, reprenez ce dossier avec l'enseignant.

Ouvrez **travail-python** dans l'éditeur utilisé en cours. Gardez le terminal
dans ce dossier. L'enseignant montre comment ouvrir un fichier, l'enregistrer
et ouvrir un terminal dans ce dossier avant de commencer.

Les projets créés pendant le TD seront à côté de `manip`, **en dehors du
dépôt du cours**. Commencez ensuite [le TD 1](td-enonces.md).

## Rendre votre travail

Travaillez sur votre propre copie. Ne poussez rien sur ce dépôt : il est en
lecture seule pour vous, et vos réponses se rendent par le canal indiqué en
séance.

## Corrigés

Les corrigés ne sont pas dans ce dépôt, sur aucune branche. Ils sont publiés,
quand ils le sont, sur le site du cours.
