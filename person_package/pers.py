# Importation des bibliothèques nécessaires
import cv2  # OpenCV pour le traitement d'image
from utils import bbox_utils as bu, pixel_utils as pu  # Utilitaires personnalisés pour les boîtes englobantes et les pixels
import numpy as np  # NumPy pour les opérations numériques
import time  # Module time pour les opérations temporelles

class Person:
    def __init__(self, id, bbox, frame, mini_map, keypoints):
        """
        Initialise une nouvelle instance de la classe Person.

        :param id: Identifiant unique de la personne
        :param bbox: Boîte englobante autour de la personne (x1, y1, x2, y2)
        :param frame: Image ou trame vidéo actuelle
        :param mini_map: Carte miniature pour le suivi
        :param keypoints: Points clés pour le mappage
        """
        self.hum_id = id  # Identifiant de la personne
        self.bbox = bbox  # Boîte englobante
        self.color = self.__generate_color()  # Génère une couleur aléatoire pour la personne
        self.converted_coord = self.__get_mapped_point(frame, mini_map, keypoints, draw=False)  # Coordonnées converties sur la mini-carte

    def get_converted_coord(self):
        """
        Retourne les coordonnées converties de la personne sur la mini-carte.

        :return: Coordonnées converties
        """
        return self.converted_coord

    def get_color(self):
        """
        Retourne la couleur associée à la personne.

        :return: Couleur sous forme de tuple (R, G, B)
        """
        return self.color

    def get_id(self):
        """
        Retourne l'identifiant de la personne.

        :return: Identifiant de la personne
        """
        return self.hum_id

    def __generate_color(self):
        """
        Génère une couleur aléatoire pour la personne.

        :return: Couleur sous forme de tuple (R, G, B)
        """
        return tuple(np.random.randint(0, 255, size=3).tolist())

    def __str__(self):
        """
        Retourne une représentation sous forme de chaîne de caractères de la personne.

        :return: Chaîne de caractères décrivant la personne
        """
        return f"Pers {self.hum_id} at {self.bbox} with color {self.color}"

    def __draw_bboxes_stream(self, frame):
        """
        Dessine la boîte englobante et l'identifiant de la personne sur la trame.

        :param frame: Image ou trame vidéo actuelle
        """
        x1, y1, x2, y2 = self.bbox
        cv2.putText(frame, f"ID: {self.hum_id}", (int(self.bbox[0]), int(self.bbox[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.2,
                    (255, 255, 255), 1)
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), self.color, 2)

    def drawBBOX(self, frame):
        """
        Dessine la boîte englobante de la personne sur la trame si elle n'a pas déjà été dessinée.

        :param frame: Image ou trame vidéo actuelle
        """
        drawn_player_bboxes = set()
        if self.hum_id not in drawn_player_bboxes:
            self.__draw_bboxes_stream(frame)
            drawn_player_bboxes.add(self.hum_id)

    def __get_mapped_point(self, frame, mini_map, keypoints, draw):
        """
        Calcule les coordonnées mappées de la personne sur la mini-carte.

        :param frame: Image ou trame vidéo actuelle
        :param mini_map: Carte miniature pour le suivi
        :param keypoints: Points clés pour le mappage
        :param draw: Indique si le dessin doit être effectué
        :return: Coordonnées mappées ou None si le mappage échoue
        """
        position = bu.get_center(self.bbox)
        ratioh, ratiov = pu.get_axes_x_y_intersection_ratio(frame, position, keypoints, draw)

        if ratioh is not None and ratiov is not None:
            point = (
                int(mini_map.map_start_x + ratioh * (mini_map.draw_rect_width - 2 * mini_map.padding_map)),
                int(mini_map.map_start_y + ratiov * (mini_map.draw_rect_height - 2 * mini_map.padding_map))
            )
            return point
        return None

    def __drawOnMiniMap(self, frame, pos):
        """
        Dessine la position de la personne sur la mini-carte.

        :param frame: Image ou trame vidéo actuelle
        :param pos: Dictionnaire contenant la position et la couleur
        :return: Trame avec la position dessinée
        """
        position = pos['point']
        color = pos['color']
        if position is not None:
            x = int(position[0])
            y = int(position[1])

            """
            # Code commenté pour ajuster la position si elle dépasse les limites de la mini-carte
            if x < self.map_start_x - self.padding_map:
                position = (self.map_start_x - self.padding_map, y)
            if x > self.map_end_x + self.padding_map:
                position = (self.map_end_x + self.padding_map, y)
            if y < self.map_start_y - self.padding_map:
                position = (x, self.map_start_y - self.padding_map)
            if y > self.map_end_y + self.padding_map:
                position = (x, self.map_end_y + self.padding_map)
            """

            cv2.rectangle(frame,
                          (int(position[0] - 2), int(position[1] - 2)),  # Point supérieur gauche
                          (int(position[0] + 2), int(position[1] + 2)),  # Point inférieur droit
                          color,  # Couleur (B, G, R)
                          -1)
            # cv2.putText(frame, f"ID: {id}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255, 255, 255), 1)
        return frame
