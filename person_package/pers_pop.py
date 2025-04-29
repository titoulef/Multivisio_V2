import numpy as np  # Importation de la bibliothèque NumPy pour les opérations numériques

class PersPop:
    def __init__(self, inactive_threshold=5):
        """
        Initialise une nouvelle instance de la classe PersPop.

        :param inactive_threshold: Délai avant qu'une personne soit considérée comme inactive (en secondes), par défaut 5 secondes
        """
        self.pop = []  # Liste pour stocker les objets Person
        self.inactive_threshold = inactive_threshold  # Délai avant désactivation (en secondes)
        self.historic_ids = {}  # Dictionnaire pour associer les IDs des personnes à leurs couleurs

    def __str__(self):
        """
        Retourne une représentation sous forme de chaîne de caractères de la population.

        :return: Chaîne de caractères décrivant chaque personne dans la population
        """
        return '\n'.join(str(person) for person in self.pop)

    def add(self, pers):
        """
        Ajoute une personne à la population.

        :param pers: Objet Person à ajouter
        """
        self.pop.append(pers)  # Ajoute la personne à la liste
        if pers.hum_id not in self.historic_ids:
            self.historic_ids[pers.hum_id] = pers.color  # Associe la couleur à l'ID si ce n'est pas déjà fait
        else:
            pers.color = self.historic_ids[pers.hum_id]  # Réutilise la couleur existante pour l'ID

    def clear(self):
        """
        Vide la population en supprimant toutes les personnes.
        """
        self.pop = []

    def __iter__(self):
        """
        Retourne un itérateur pour parcourir la population.

        :return: Itérateur sur la liste des personnes
        """
        return iter(self.pop)
