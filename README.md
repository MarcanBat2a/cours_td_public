# Chapitre 2 - Rappel des structures algorithmiques

**UE 0 - Algo 3 avec Python** · TD et matériel de séance
Boucles, conditions, tris et récursivité en Python

Branche : `tp/ue0-02-structures-algorithmiques`

## Récupérer le TD

```bash
git clone https://github.com/MarcanBat2a/cours_td_public.git
cd cours_td_public
git switch tp/ue0-02-structures-algorithmiques
```

## Récupérer une nouvelle version sans perdre ses réponses

Les branches de TD sont remplacées lors des corrections. Si vous avez déjà
utilisé celle-ci, `git fetch` puis `git switch` ne mettent pas à jour votre
branche locale. Gardez votre copie et vos réponses, puis téléchargez la
version actuelle dans **un nouveau dossier**.

Depuis le dossier qui contient votre copie actuelle :

```bash
git clone --single-branch --branch tp/ue0-02-structures-algorithmiques \
  https://github.com/MarcanBat2a/cours_td_public.git cours-td-chapitre2-v2
```

Si `cours-td-chapitre2-v2` existe déjà, choisissez un nom libre (`v3`, etc.).
Comparez le nouvel énoncé et les fichiers de `manip/` avec votre travail
dans `algo3/chapitre2/`, puis reportez les changements utiles. Vos fonctions
et vos réponses restent dans leur dossier de travail.

## Ce que contient la branche

- `cours.md` - les définitions et les exemples expliqués, notamment les traces pas à pas
- `manip/` - les fichiers à utiliser pendant la séance sur machine
- `memo-a4.md` - le mémo de syntaxe - la matière de la feuille A4 autorisée à l'épreuve
- `td-enonces.md` - l'énoncé des travaux dirigés
- `td-donjon.md` - la variante facultative « donjon », à choisir à la place des communes ; fichiers dans `manip/donjon/`, exploration en bonus

Chaque chapitre a sa branche : `git switch tp/<ue>-<chapitre>`. La branche
`master` en donne la liste.

## Rendre votre travail

Travaillez sur votre propre copie. Ne poussez rien sur ce dépôt : il est en
lecture seule pour vous, et vos réponses se rendent par le canal indiqué en
séance.

## Corrigés

Les corrigés ne sont pas dans ce dépôt, sur aucune branche. Ils sont publiés,
quand ils le sont, sur le site du cours.

## Progresser dans le chapitre

Lire l’exemple du cours, faire la trace sur papier, compléter le programme,
puis résoudre l’exercice autonome. Les ressources de qkzk (première et
terminale) sont référencées à la fin de `cours.md`. Les formules de
complexité sont étudiées dans la branche du chapitre 3.
