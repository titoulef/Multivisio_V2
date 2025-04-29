# Importation des bibliothèques nécessaires
import cv2  # Bibliothèque OpenCV pour le traitement d'images et de vidéos
from utils import bbox_utils as bu, pixel_utils as pu  # Importation des utilitaires pour les boîtes englobantes et les pixels

class Suit:
    def __init__(self, id, bbox, frame, mini_map, keypoints):
        """
        Initialise une nouvelle instance de la classe Suit.

        :param id: Identifiant unique de la valise.
        :param bbox: Coordonnées de la boîte englobante de la valise (x1, y1, x2, y2).
        :param frame: Image ou trame vidéo actuelle.
        :param mini_map: Carte miniature pour le suivi.
        :param keypoints: Points clés pour le mappage des coordonnées.
        """
        self.suit_id = id  # Identifiant unique de la valise
        self.bbox = bbox  # Coordonnées de la boîte englobante
        self.color = (0, 0, 255)  # Couleur par défaut pour dessiner la boîte englobante (rouge)
        self.converted_coord = self.__get_mapped_point(frame, mini_map, keypoints, draw=False)  # Coordonnées converties sur la mini-carte
        self.lost = False  # Indicateur si la valise est perdue

    def get_converted_coord(self):
        """
        Retourne les coordonnées converties de la valise sur la mini-carte.

        :return: Coordonnées converties.
        """
        return self.converted_coord

    def get_color(self):
        """
        Retourne la couleur actuelle de la boîte englobante.

        :return: Couleur de la boîte englobante.
        """
        return self.color

    def get_id(self):
        """
        Retourne l'identifiant unique de la valise.

        :return: Identifiant de la valise.
        """
        return self.suit_id

    def __str__(self):
        """
        Retourne une représentation sous forme de chaîne de caractères de l'objet Suit.

        :return: Chaîne de caractères représentant la valise.
        """
        return f"Suitcase {self.suit_id} at {self.bbox}"

    def __draw_bboxes_stream(self, frame):
        """
        Dessine la boîte englobante de la valise sur la trame donnée.

        :param frame: Trame vidéo sur laquelle dessiner.
        """
        x1, y1, x2, y2 = self.bbox
        # Dessine le texte "LOST" si la valise est perdue
        if self.lost:
            cv2.putText(frame, f"LOST", (int(self.bbox[0]), int(self.bbox[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0, 0, 255), 1)
        # Dessine le rectangle de la boîte englobante
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), self.color, 2)

    def drawBBOX(self, frame, lien_dict, pers_pop):
        """
        Dessine la boîte englobante de la valise en fonction des associations avec les joueurs.

        :param frame: Trame vidéo sur laquelle dessiner.
        :param lien_dict: Dictionnaire des associations entre valises et joueurs.
        :param pers_pop: Liste des joueurs.
        """
        drawn_bboxes = set()  # Ensemble pour garder une trace des valises déjà dessinées

        # Si la valise est associée à un joueur, utiliser la couleur du joueur
        if self.suit_id in lien_dict:
            player_id = lien_dict[self.suit_id]  # ID du joueur associé à la valise

            # Trouver le joueur correspondant dans pers_pop
            for player in pers_pop:
                if player.hum_id == player_id:
                    self.color = player.color  # Utiliser la couleur du joueur
                    break

        # Dessiner la boîte englobante de la valise si elle n'a pas déjà été dessinée
        if self.suit_id not in drawn_bboxes:
            self.__draw_bboxes_stream(frame)
            drawn_bboxes.add(self.suit_id)

    def __get_mapped_point(self, frame, mini_map, keypoints, draw):
        """
        Convertit les coordonnées de la valise sur la mini-carte.

        :param frame: Trame vidéo actuelle.
        :param mini_map: Carte miniature pour le suivi.
        :param keypoints: Points clés pour le mappage des coordonnées.
        :param draw: Indicateur pour savoir si le dessin est activé.
        :return: Coordonnées converties sur la mini-carte.
        """
        position = bu.get_center(self.bbox)  # Obtient le centre de la boîte englobante
        ratioh, ratiov = pu.get_axes_x_y_intersection_ratio(frame, position, keypoints, draw)  # Calcule les ratios pour le mappage

        if ratioh is not None and ratiov is not None:
            point = (
                int(mini_map.map_start_x + ratioh * (mini_map.draw_rect_width - 2 * mini_map.padding_map)),
                int(mini_map.map_start_y + ratiov * (mini_map.draw_rect_height - 2 * mini_map.padding_map))
            )
            return point
        return None

