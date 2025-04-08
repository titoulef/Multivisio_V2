class SuitPop():
    def __init__(self):
        self.pop=[]

    def __str__(self):
        return '\n'.join(str(suit) for suit in self.pop)

    def clear(self):
        self.pop=[]

    def add(self, suit):
        self.pop.append(suit)  # Ajoute le Suit s'il n'existe pas déjà


    def __iter__(self):
        return iter(self.pop)