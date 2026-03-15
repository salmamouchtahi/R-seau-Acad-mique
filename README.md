Réseau Social Académique – Basé sur les Graphes

Description du projet : 

Ce projet modélise un réseau académique sous forme de graphe non orienté.
Les chercheurs sont représentés comme des sommets.
Les collaborations sont représentées comme des arêtes.
Le système permet d’ajouter, supprimer et analyser les relations entre chercheurs.
Une interface graphique interactive permet de visualiser le réseau et générer un rapport PDF.

Structure du projet :

1.reseau_academique.py :
Contient la classe ReseauAcademique qui implémente :
la structure du graphe avec un dictionnaire de sets
la gestion des chercheurs
la gestion des collaborations
le calcul des degrés
le parcours DFS
la détection des composantes connexes
un système de suggestion de collaborations

2.app.py:
l’interface graphique développée avec Streamlit :
visualisation interactive du graphe avec NetworkX et Pyvis
calcul de centralité
affichage des statistiques
export automatique d’un rapport PDF
Structure de données utilisée

Le graphe est représenté par :
self.graphe: Dict[str, Set[str]] = defaultdict(set)
La clé du dictionnaire représente un chercheur.
La valeur est un set contenant ses collaborateurs.
Le set permet d’éviter les doublons automatiquement.
Le dictionnaire permet un accès rapide aux voisins d’un chercheur.

Fonctionnalités principales :

Ajouter / supprimer un chercheur
Ajouter / supprimer une collaboration
Calcul du degré d’un chercheur
Identification du chercheur le plus central
Détection des composantes connexes (DFS)
Suggestions de collaborations basées sur les amis en commun
Visualisation interactive du graphe
Export d’un rapport PDF complet

Technologies utilisées :

Python 3
Streamlit
NetworkX
Pyvis
Community Louvain (détection de communautés)
Matplotlib
ReportLab (génération PDF)
Structures de données : dictionnaire, set
Algorithmes : DFS

Comment exécuter le projet:

1.Installer les dépendances : 
pip install streamlit networkx pyvis python-louvain matplotlib reportlab

2.Lancer l’application : 
streamlit run app.py
L’application s’ouvrira automatiquement dans le navigateur.

Remarques importantes:

Le graphe est non orienté : chaque collaboration est enregistrée dans les deux sens.
Le DFS est implémenté de manière itérative avec une pile
Les suggestions de collaboration sont basées sur le nombre d’amis en commun.