from collections import defaultdict
from typing import Dict, Set, List


class ReseauAcademique:
    """
    Graphe non orienté représentant un réseau académique.
    Sommets : chercheurs
    Arêtes : collaborations
    """

    def __init__(self):
        self.graphe: Dict[str, Set[str]] = defaultdict(set)

    # ==========================
    # Gestion des chercheurs
    # ==========================

    def ajouter_chercheur(self, nom: str) -> None:
        if nom in self.graphe:
            raise ValueError(f"Le chercheur '{nom}' existe déjà.")
        self.graphe[nom] = set()

    def supprimer_chercheur(self, nom: str) -> None:
        if nom not in self.graphe:
            raise ValueError(f"Le chercheur '{nom}' n'existe pas.")

        # Supprimer toutes ses collaborations
        for voisin in self.graphe[nom]:
            self.graphe[voisin].remove(nom)

        del self.graphe[nom]

    # ==========================
    # Gestion des collaborations
    # ==========================

    def ajouter_collaboration(self, c1: str, c2: str) -> None:
        if c1 not in self.graphe or c2 not in self.graphe:
            raise ValueError("Un des chercheurs n'existe pas.")

        if c1 == c2:
            raise ValueError("Un chercheur ne peut pas collaborer avec lui-même.")

        self.graphe[c1].add(c2)
        self.graphe[c2].add(c1)

    def supprimer_collaboration(self, c1: str, c2: str) -> None:
        if c1 not in self.graphe or c2 not in self.graphe:
            raise ValueError("Un des chercheurs n'existe pas.")

        self.graphe[c1].discard(c2)
        self.graphe[c2].discard(c1)

    # ==========================
    # Mesures simples
    # ==========================

    def degre(self, nom: str) -> int:
        if nom not in self.graphe:
            raise ValueError(f"Le chercheur '{nom}' n'existe pas.")
        return len(self.graphe[nom])

    def degres_tous(self) -> Dict[str, int]:
        return {chercheur: len(voisins) for chercheur, voisins in self.graphe.items()}

    def chercheur_plus_central(self) -> str:
        if not self.graphe:
            return None
        return max(self.graphe, key=lambda x: len(self.graphe[x]))

    # ==========================
    # Parcours et composantes
    # ==========================

    def _dfs(self, depart: str, visites: Set[str]) -> Set[str]:
        pile = [depart]
        composante = set()

        while pile:
            courant = pile.pop()
            if courant not in visites:
                visites.add(courant)
                composante.add(courant)
                pile.extend(self.graphe[courant] - visites)

        return composante

    def composantes_connexes(self) -> List[Set[str]]:
        visites = set()
        composantes = []

        for chercheur in self.graphe:
            if chercheur not in visites:
                composante = self._dfs(chercheur, visites)
                composantes.append(composante)

        return composantes

    # ==========================
    # Suggestion intelligente
    # ==========================

    def suggestion_collaborations(self, nom: str) -> List[str]:
        """
        Propose des collaborations basées sur le nombre d'amis en commun.
        """
        if nom not in self.graphe:
            raise ValueError(f"Le chercheur '{nom}' n'existe pas.")

        suggestions = defaultdict(int)
        voisins = self.graphe[nom]

        for voisin in voisins:
            for voisin_du_voisin in self.graphe[voisin]:
                if (
                    voisin_du_voisin != nom
                    and voisin_du_voisin not in voisins
                ):
                    suggestions[voisin_du_voisin] += 1

        # Trier par nombre d'amis en commun décroissant
        return sorted(suggestions, key=suggestions.get, reverse=True)

    # ==========================
    # Affichage
    # ==========================

    def afficher(self) -> None:
        for chercheur, voisins in self.graphe.items():
            print(f"{chercheur} -> {list(voisins)}")




