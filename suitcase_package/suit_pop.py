class SuitPop:
    def __init__(self):
        """
        Initialise une nouvelle instance de la classe SuitPop.
        Cette classe gère une collection de valises (objets Suit).
        """
        self.pop = []  # Liste pour stocker les objets Suit

    def __str__(self):
        """
        Retourne une représentation sous forme de chaîne de caractères de la collection de valises.
        Chaque valise est représentée sur une nouvelle ligne.

        :return: Chaîne de caractères représentant la collection de valises.
        """
        return '\n'.join(str(suit) for suit in self.pop)

    def clear(self):
        """
        Vide la collection de valises.
        """
        self.pop = []

    def add(self, suit):
        """
        Ajoute une valise à la collection.

        :param suit: Objet Suit à ajouter à la collection.
        """
        self.pop.append(suit)  # Ajoute le Suit s'il n'existe pas déjà

    def __iter__(self):
        """
        Retourne un itérateur pour parcourir la collection de valises.

        :return: Itérateur sur la collection de valises.
        """
        return iter(self.pop)
