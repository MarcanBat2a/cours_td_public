"use strict";
const MISSIONS = [
  {
    id: 1, titre: "Le cadeau de dernière minute", court: "Trouver le bon cadeau", minutes: 15,
    concept: "Filtrer, projeter et trier un catalogue de documents",
    personne: "Inès, première cliente", histoire: "J'ai 35 € pour offrir un livre. Je veux repartir avec aujourd'hui. Vous avez quelque chose ? Montrez-moi seulement le nom et le prix, du moins cher au plus cher.",
    taches: ["Explorez les sept produits de cours.produits avec un premier find.", "Écrivez un filtre qui respecte les trois demandes d'Inès.", "Choisissez une projection et un tri. Prédisez les résultats avant d'exécuter."],
    preuve: "Votre requête, les noms et prix des produits retenus et une phrase expliquant pourquoi un livre numérique ne suffit pas à prouver une disponibilité physique.",
    indices: ["Le prix est un nombre. Plusieurs champs dans un même filtre sont combinés par ET.", "Le livre numérique n'a pas de champ stock. Une quantité strictement positive distingue le livre physique disponible.", "Dans la console, séparez filter, projection et sort. $lte inclut la borne, $gt l'exclut."],
    moteur: "mongo", base: "cours", collection: "produits", operation: "find", depart: {filter: {}, projection: {}, sort: {}, limit: 10}
  },
  {
    id: 2, titre: "Le vêtement fantôme", court: "Démasquer un faux stock", minutes: 20,
    concept: "Deux conditions, un seul élément de tableau : $elemMatch",
    personne: "Karim, à la cabine", histoire: "Votre site dit que le T-shirt existe en M et qu'il en reste. Dans le rayon, le M est épuisé. Je me suis déplacé pour rien ?",
    taches: ["Testez le filtre proposé. Regardez chaque variante de T-100 et T-200.", "Identifiez pourquoi le filtre accepte un produit dont le M est épuisé.", "Réparez la requête afin qu'une même variante soit en M et disponible."],
    preuve: "Les résultats avant et après, votre filtre réparé et l'identification des deux variantes qui trompaient la première requête.",
    indices: ["Une condition sur variantes.taille et une autre sur variantes.stock peuvent être satisfaites par deux éléments différents.", "$elemMatch place les deux conditions dans le même objet associé au tableau variantes.", "À l'intérieur de $elemMatch, les champs sont taille et stock, sans le préfixe variantes."],
    moteur: "mongo", base: "cours", collection: "produits", operation: "find", depart: {filter: {"variantes.taille": "M", "variantes.stock": {$gt: 0}}, limit: 10}
  },
  {
    id: 3, titre: "L'import qui avait tout mélangé", court: "Enquêter sur les types", minutes: 25,
    concept: "Types BSON, schéma souple, stock absent et null",
    personne: "Lina, au support", histoire: "Des produits disparaissent des filtres de prix. Et notre équipe appelle tout ce qui n'est pas disponible « rupture ». Les précommandes et les ebooks aussi !",
    taches: ["Dans boutique.produits, comptez les produits par type de prix avec une agrégation, puis retrouvez les prix stockés en texte.", "Réparez uniquement ces prix avec updateMany et un pipeline de conversion. Contrôlez les types, puis rejouez la réparation et comparez les compteurs.", "Dans cours.produits, distinguez un stock à zéro, un stock explicitement null et un champ stock absent. Testez aussi {stock: null}."],
    preuve: "Le nombre d'anomalies avant et après, la modification ciblée et trois filtres qui distinguent les états de stock. Expliquez ce que prouve le résultat de {stock: null}.",
    indices: ["Un filtre $type peut chercher les string. La console affiche total même si elle ne montre que 50 documents.", "Un pipeline de mise à jour est un tableau d'étapes. $toInt peut convertir la valeur de l'ancien champ, référencé par $prix.", "$exists distingue l'absence du champ. $type: \"null\" recherche une valeur explicitement null."],
    moteur: "mongo", base: "boutique", collection: "produits", operation: "find", depart: {filter: {}, projection: {_id: 1, prix: 1}, limit: 10}
  },
  {
    id: 4, titre: "Qui finance les pizzas ?", court: "Faire parler les ventes", minutes: 25,
    concept: "Pipeline : $match, $unwind, $group, $multiply et $sort",
    personne: "La responsable du Pop-up", histoire: "On fête l'ouverture ce soir. Pour décider quoi mettre en avant, j'ai besoin du chiffre d'affaires par produit, seulement pour les commandes expédiées ou livrées. Les paniers en préparation ne comptent pas.",
    taches: ["Parcourez les quatre commandes de cours.commandes et choisissez les statuts retenus.", "Calculez les ventes par produit à partir des lignes et du prix effectivement payé.", "Classez les produits par chiffre d'affaires décroissant. Vérifiez un produit à la main."],
    preuve: "Le pipeline, le classement, un calcul manuel et l'explication de l'ordre des étapes. Dites pourquoi le prix actuel du catalogue ne doit pas remplacer le prix de la ligne.",
    indices: ["Une commande contient plusieurs lignes. $unwind produit une entrée par ligne avant le regroupement.", "La recette d'une ligne vaut lignes.prix multiplié par lignes.quantite. Le groupe utilise lignes.produit.", "Écartez d'abord les commandes non retenues. $sum peut accumuler une expression $multiply, et $sort vient après le groupe."],
    moteur: "mongo", base: "cours", collection: "commandes", operation: "aggregate", depart: {pipeline: []}
  },
  {
    id: 5, titre: "Le rayon qui lit toute la boutique", court: "Réduire les lectures", minutes: 25,
    concept: "explain, COLLSCAN, IXSCAN et index composé",
    personne: "Hugo, à la caisse", histoire: "Je cherche les produits audio à 150 € maximum, du moins cher au plus cher. La boutique contient 20 000 fiches. Peut-on éviter de toutes les lire à chaque demande ?",
    taches: ["Construisez ce filtre dans boutique.produits et triez par prix, puis _id pour départager les ex aequo. Affichez les dix premiers avec find.", "Exécutez explain sans limit pour mesurer la requête complète. Relevez nReturned, totalDocsExamined et totalKeysExamined.", "Créez un index adapté à l'égalité et au tri, puis mesurez à nouveau. Préservez les résultats."],
    preuve: "Les deux mesures, l'index choisi et une justification de l'ordre des champs. Comparez le travail évité, même si les durées sont très petites.",
    indices: ["Gardez le filtre et le tri de find mais retirez limit pour mesurer toute la requête avec explain. Les compteurs sont dans executionStats.", "Un index composé suit l'ordre de ses champs. L'égalité sur categorie peut précéder le parcours ordonné par prix.", "Le tri demandé contient aussi _id. Recherchez les étapes à l'intérieur du plan, pas seulement dans son premier niveau."],
    moteur: "mongo", base: "boutique", collection: "produits", operation: "explain", depart: {filter: {}, sort: {}}
  },
  {
    id: 6, titre: "Une lettre perdue, un client retrouvé", court: "Chercher malgré une faute", minutes: 15,
    concept: "Analyse du texte, index inversé et match avec fuzziness",
    personne: "Inès, sur son téléphone", histoire: "J'ai tapé « casqe » dans votre recherche. Aucun résultat. Pourtant votre vitrine montre un casque ! Comment la recherche lit-elle mes mots ?",
    taches: ["Envoyez Casque Nomade à /catalogue/_analyze avec l'analyseur standard. Observez les termes.", "Cherchez casqe dans nom avec match, sans tolérance puis avec fuzziness: AUTO.", "Expliquez ce qui change et pourquoi la catégorie est mappée en keyword."],
    preuve: "Les termes analysés, les deux recherches et les résultats observés. Ne mémorisez pas de score numérique.",
    indices: ["Dans la console HTTP, méthode, chemin et corps sont trois informations séparées.", "La forme longue de match accepte query et fuzziness dans l'objet du champ nom.", "La tolérance n'est pas activée automatiquement. text analyse des mots, keyword conserve une valeur entière."],
    moteur: "elastic", method: "POST", path: "/catalogue/_analyze", depart: {analyzer: "standard", text: "Casque Nomade"}
  },
  {
    id: 7, titre: "La bonne recherche au bon budget", court: "Combiner recherche et filtres", minutes: 20,
    concept: "bool : pertinence dans must, contraintes dans filter",
    personne: "Karim, futur acheteur", histoire: "Je veux un « casque nomade », dans le rayon audio, à moins de 150 €. Je ne veux pas qu'un bon score fasse passer un produit hors budget.",
    taches: ["Inspectez /catalogue/_mapping, puis combinez match sur nom, term sur categorie et range sur prix.", "Placez la recherche dans must et les contraintes exactes dans filter. Changez seulement le budget pour imposer un prix inférieur à 100 € et observez.", "Expliquez le OU par défaut de match et l'effet de operator: and. Bonus : construisez une facette de catégories avec une agrégation terms."],
    preuve: "La recherche complète, les résultats et une phrase séparant score et critères obligatoires. Avec seulement sept produits, un même résultat ne prouve pas que OU et ET sont équivalents.",
    indices: ["bool combine des clauses. must contribue au score, filter impose les critères sans y contribuer.", "term est adapté à la catégorie keyword. Un intervalle de prix utilise range et ici lt.", "match analyse le texte et combine ses mots avec OU par défaut. operator: and exige tous les termes."],
    moteur: "elastic", method: "POST", path: "/catalogue/_search", depart: {query: {match_all: {}}, size: 10}
  },
  {
    id: 8, titre: "Deux clients, le dernier casque", court: "Sauver l'ouverture", minutes: 20,
    concept: "Atomicité MongoDB, copie de recherche et refresh Elasticsearch",
    personne: "Alice et Karim, devant le dernier A-400", histoire: "Nous voyons tous les deux « disponible » dans la recherche. Il n'en reste qu'un. À qui pouvez-vous confirmer l'achat, et que doit faire la boutique pour que la recherche rattrape le stock ?",
    taches: ["Préparez la scène à stock 1 et inspectez les deux stocks. Écrivez l'updateOne atomique dans le carnet, sans l'exécuter avant les boutons d'achat.", "Déclenchez les demandes d'Alice et de Karim. Lisez matchedCount et le stock restant : quel filtre empêche un stock négatif ?", "Essayez un refresh Elasticsearch, puis une copie depuis MongoDB. Identifiez les deux opérations et justifiez la source vérifiée à l'achat."],
    preuve: "Les deux réponses d'achat, les stocks après achat, après refresh et après copie, ainsi que votre écriture MongoDB conditionnelle. Pour finir : où ranger variantes, avis et prix payé d'une commande ?",
    indices: ["Le stock doit être testé dans le filtre de l'updateOne, et décrémenté dans cette même opération.", "matchedCount à zéro signifie ici rupture de stock, même si la requête a correctement fonctionné.", "Le refresh rend visibles des écritures déjà reçues par Elasticsearch. Il ne lit pas MongoDB. La synchronisation transmet les changements et reproduit aussi les suppressions."],
    moteur: "mongo", base: "cours", collection: "produits", operation: "find", depart: {filter: {_id: "A-400"}}
  }
];
