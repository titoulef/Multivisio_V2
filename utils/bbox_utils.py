import numpy as np
import cv2
import random
import os


def get_center(bbox):
    """
    Calcule le point central en bas d'une boîte englobante.

    Args:
        bbox (tuple): Coordonnées de la boîte englobante (x1, y1, x2, y2)

    Returns:
        tuple: Coordonnées (x, y) du point central en bas
    """
    x1, y1, x2, y2 = bbox
    cx = int((x1 + x2) / 2)  # Centre horizontal
    cy = int(y2)  # Bas de la boîte
    return (cx, cy)


def get_distance(p1, p2):
    """
    Calcule la distance euclidienne entre deux points.

    Args:
        p1 (tuple): Coordonnées du premier point (x1, y1)
        p2 (tuple): Coordonnées du deuxième point (x2, y2)

    Returns:
        float: Distance entre les deux points
    """
    x1, y1 = p1
    x2, y2 = p2
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def bbox_distance(bbox1, bbox2):
    """
    Calcule la distance entre les centres de deux boîtes englobantes.

    Args:
        bbox1 (tuple): Première boîte englobante (x1, y1, x2, y2)
        bbox2 (tuple): Deuxième boîte englobante (x1, y1, x2, y2)

    Returns:
        float: Distance entre les centres des boîtes
    """
    c1 = get_center(bbox1)
    c2 = get_center(bbox2)
    distance = get_distance(c1, c2)
    return distance


def bbox_covering(bbox1, bbox2, threshold=0.05, type='center'):
    """
    Vérifie si deux boîtes englobantes se chevauchent selon différents critères.

    Args:
        bbox1 (tuple): Première boîte englobante
        bbox2 (tuple): Deuxième boîte englobante
        threshold (float): Seuil de chevauchement (par défaut 0.05)
        type (str): Méthode de vérification ('intersection' ou 'center')

    Returns:
        bool: True si les boîtes se chevauchent selon le critère choisi
    """
    if type == 'intersection':
        # Méthode par intersection des surfaces
        x1, y1, x2, y2 = bbox1
        x3, y3, x4, y4 = bbox2

        # Augmentation de la boîte englobante de la valise
        delta = abs(x4 - x3) * 0.25
        x3 -= delta
        y3 -= delta
        x4 += delta
        y4 += delta

        # Calcul des aires
        area_person = abs(x2 - x1) * abs(y2 - y1)
        area_suitcase = abs(x4 - x3) * abs(y4 - y3)

        # Calcul de la zone d'intersection
        xleft = max(x1, x3)
        xright = min(x2, x4)
        ytop = max(y1, y3)
        ybottom = min(y2, y4)

        # Vérification d'intersection
        if xright < xleft or ybottom < ytop:
            return False  # Pas d'intersection

        # Calcul de la surface d'intersection
        deltax = xright - xleft
        deltay = ybottom - ytop
        intersection = deltax * deltay

        # Vérification du seuil
        return intersection > threshold * area_suitcase

    elif type == 'center':
        # Méthode par distance des centres
        distance = bbox_distance(bbox1, bbox2)
        height = bbox1[3] - bbox1[1]  # Hauteur de la première boîte
        return distance <= 0.5 * height


def associate_objects(pers_pop, suitcase_pop, radius_in_pixels):
    """
    Associe les valises aux personnes selon leur proximité.

    Args:
        pers_pop (PersPop): Population de personnes à suivre
        suitcase_pop (SuitPop): Population de valises à suivre
        radius_in_pixels (float): Rayon maximum d'association en pixels

    Returns:
        dict: Dictionnaire des associations {id_valise: id_personne}
    """
    lien_dict = {}  # Dictionnaire pour stocker les associations

    # Parcours de toutes les valises
    for suitcase in suitcase_pop.pop:
        coord_suit = suitcase.get_converted_coord()  # Position de la valise

        if coord_suit is None:
            continue  # Si la valise n'a pas de position valide

        # Recherche de la personne la plus proche
        for player in pers_pop.pop:
            coord_pers = player.get_converted_coord()  # Position de la personne

            if coord_pers is None:
                continue  # Si la personne n'a pas de position valide

            # Vérification de la distance
            if get_distance(coord_suit, coord_pers) <= radius_in_pixels:
                # Association trouvée
                lien_dict[suitcase.suit_id] = player.hum_id
                suitcase.lost = False  # Marque la valise comme trouvée
                break  # Passe à la valise suivante
            else:
                suitcase.lost = True  # Marque la valise comme perdue
                print(f"{suitcase} perdu")  # Log de débogage

    return lien_dict