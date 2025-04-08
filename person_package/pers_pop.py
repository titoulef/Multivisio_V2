import numpy as np

class PersPop:
    def __init__(self, inactive_threshold=5):
        self.pop = []  # Liste pour stocker les personnes
        self.inactive_threshold = inactive_threshold  # Délai avant désactivation (en secondes)
        self.historic_ids = {}  # Dictionnaire pour associer les IDs aux couleurs

    def __str__(self):
        return '\n'.join(str(person) for person in self.pop)

    def add(self, pers):
        self.pop.append(pers)
        if pers.hum_id not in self.historic_ids:
            self.historic_ids[pers.hum_id] = pers.color
        else:
            pers.color = self.historic_ids[pers.hum_id]


    def clear(self):
        self.pop = []

    def __iter__(self):
        return iter(self.pop)