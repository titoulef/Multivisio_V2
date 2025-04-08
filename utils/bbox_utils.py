import numpy as np
import cv2
import random
import os


def get_center(bbox):
    x1, y1, x2, y2 = bbox
    cx=int((x1+x2)/2)
    cy=int(y2)
    return (cx, cy)

def get_distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return np.sqrt((x2-x1)**2 + (y2-y1)**2)


def bbox_distance(bbox1, bbox2):
    c1=get_center(bbox1)
    c2=get_center(bbox2)
    distance = get_distance(c1, c2)
    return distance

def bbox_covering(bbox1, bbox2, threshold=0.05, type='center'):
    if type == 'intersection':
        x1, y1, x2, y2 = bbox1
        x3, y3, x4, y4 = bbox2
        delta = abs(x4-x3)*0.25  # augmentation de la bbox suitcase
        x3-=delta
        y3-=delta
        x4+=delta
        y4+=delta
        # Ensure areas are positive
        area_personn = abs(x2 - x1) * abs(y2 - y1)
        area_suitcase = abs(x4 - x3) * abs(y4 - y3)


        # Calculate the intersection rectangle
        xleft = max(x1, x3)
        xright = min(x2, x4)
        ytop = max(y1, y3)
        ybottom = min(y2, y4)
        if xright < xleft or ybottom < ytop:
            return False  # No intersection
        deltax = xright - xleft
        deltay = ybottom - ytop
        intersection = deltax * deltay
        # Check if the intersection covers enough of the smaller area
        if intersection > threshold * area_suitcase:
            return True
        else:
            return False

    elif type == 'center':
        distance = bbox_distance(bbox1, bbox2)
        if distance > 0.5 * (bbox1[3] - bbox1[1]):
            return False
        else:
            return True


def associate_objects(pers_pop, suitcase_pop, radius_in_pixels):
    lien_dict = {}  # Dictionnaire pour stocker les nouvelles associations


    for suitcase in suitcase_pop.pop:
        coord_suit = suitcase.get_converted_coord()  # Boîte englobante de la valise
        if coord_suit is None:
            continue

        # Parcourir chaque joueur dans player_pop
        for player in pers_pop.pop:
            coord_pers = player.get_converted_coord()   # Boîte englobante du joueur
            if coord_pers is None:
                continue
            # Vérifier si les boîtes englobantes se chevauchent (par exemple, centre de la valise dans la bbox du joueur)
            if get_distance(coord_suit, coord_pers)<=radius_in_pixels:
                # Associer la valise au joueur
                lien_dict[suitcase.suit_id] = player.hum_id
                suitcase.lost = False
                break  # Arrêter après la première association
            else:
                suitcase.lost = True
                print(str(suitcase) + " perdu")

    return lien_dict

