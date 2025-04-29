import cv2
import sys
import numpy as np

sys.path.append('../')


class MiniMap():
    def __init__(self, frame):
        """Initialise la mini-carte avec la frame de référence.

        Args:
            frame (numpy.ndarray): Image de référence pour dimensionner la mini-carte
        """
        # Marges et espacements
        self.buffer = 20  # Marge extérieure autour du fond
        self.padding_map = 10  # Marge intérieure entre le fond et la carte

        # Dimensions du rectangle de dessin (taille de la mini-carte)
        # Note: shape[0] = hauteur, shape[1] = largeur
        self.draw_rect_width = frame.shape[0] - self.buffer - self.padding_map
        self.draw_rect_height = frame.shape[1] - self.buffer - self.padding_map

        # Initialisation des positions et éléments graphiques
        self.set_canvas_background_box_position(frame)
        self.set_mini_map_position()
        self.set_map_drawing_key_points()
        self.set_map_lines()

    def set_canvas_background_box_position(self, frame):
        """Définit la position du rectangle de fond de la mini-carte.

        Positionne par défaut en haut à droite de la frame.

        Args:
            frame (numpy.ndarray): Image de référence pour le positionnement
        """
        frame = frame.copy()
        self.end_x = frame.shape[1] - self.buffer  # Coin inférieur droit (x)
        self.end_y = self.buffer + self.draw_rect_height  # Coin inférieur droit (y)
        self.start_x = self.end_x - self.draw_rect_width  # Coin supérieur gauche (x)
        self.start_y = self.end_y - self.draw_rect_height  # Coin supérieur gauche (y)

    def set_map_drawing_key_points(self):
        """Définit les 4 points clés (coins) pour le dessin de la mini-carte."""
        draw_key_points = [0] * 8  # 4 points (x,y)

        # Point haut-gauche
        draw_key_points[0], draw_key_points[1] = int(self.map_start_x), int(self.map_start_y)
        # Point haut-droite
        draw_key_points[2], draw_key_points[3] = int(self.map_end_x), int(self.map_start_y)
        # Point bas-droite
        draw_key_points[4], draw_key_points[5] = int(self.map_end_x), int(self.map_end_y)
        # Point bas-gauche
        draw_key_points[6], draw_key_points[7] = int(self.map_start_x), int(self.map_end_y)

        self.draw_key_points = draw_key_points

    def set_map_lines(self):
        """Définit les lignes à tracer entre les points clés (contour de la carte)."""
        self.lines = {
            (0, 1),  # Ligne haut (gauche -> droite)
            (1, 2),  # Ligne droite (haut -> bas)
            (2, 3),  # Ligne bas (droite -> gauche)
            (3, 0)  # Ligne gauche (bas -> haut)
        }

    def set_mini_map_position(self):
        """Calcule la position effective de la carte à l'intérieur du fond."""
        self.map_start_x = self.start_x + self.padding_map
        self.map_start_y = self.start_y + self.padding_map
        self.map_end_x = self.end_x - self.padding_map
        self.map_end_y = self.end_y - self.padding_map
        self.map_drawing_width = self.map_end_x - self.map_start_x

    def draw_map_key(self, frame):
        """Dessine les points clés et leurs labels sur la frame.

        Args:
            frame (numpy.ndarray): Image sur laquelle dessiner

        Returns:
            numpy.ndarray: Image modifiée
        """
        for i in range(0, len(self.draw_key_points), 2):
            x = int(self.draw_key_points[i])
            y = int(self.draw_key_points[i + 1])
            cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)  # Point bleu
            cv2.putText(frame, f"KP: {i // 2}", (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.2,
                        (255, 255, 255), 1)
        return frame

    def draw_map_lines(self, frame):
        """Dessine les lignes du contour de la mini-carte.

        Args:
            frame (numpy.ndarray): Image sur laquelle dessiner

        Returns:
            numpy.ndarray: Image modifiée
        """
        for line in self.lines:
            start_point = (int(self.draw_key_points[line[0] * 2]),
                           int(self.draw_key_points[line[0] * 2 + 1]))
            end_point = (int(self.draw_key_points[line[1] * 2]),
                         int(self.draw_key_points[line[1] * 2 + 1]))
            cv2.line(frame, start_point, end_point, (0, 0, 0), 1)
        return frame

    def draw_backround_rect(self, frame):
        """Dessine le rectangle de fond semi-transparent.

        Args:
            frame (numpy.ndarray): Image sur laquelle dessiner

        Returns:
            numpy.ndarray: Image modifiée
        """
        shapes = np.zeros_like(frame, np.uint8)
        # Dessin du rectangle blanc
        cv2.rectangle(shapes, (self.start_x, self.start_y),
                      (self.end_x, self.end_y), (255, 255, 255), cv2.FILLED)

        # Application de la transparence
        out = frame.copy()
        alpha = 0.5
        mask = shapes.astype(bool)
        out[mask] = cv2.addWeighted(frame, alpha, shapes, 1 - alpha, 0)[mask]
        return out

    def draw_mini_map(self, frame):
        """Dessine la mini-carte complète (fond + contour + points clés).

        Args:
            frame (numpy.ndarray): Image sur laquelle dessiner

        Returns:
            numpy.ndarray: Image modifiée
        """
        frame = self.draw_backround_rect(frame)
        frame = self.draw_map_lines(frame)
        frame = self.draw_map_key(frame)
        return frame

    def __drawOnMiniMap(self, frame, thing):
        """Méthode interne pour dessiner un objet sur la mini-carte.

        Args:
            frame (numpy.ndarray): Image sur laquelle dessiner
            thing: Objet à dessiner (doit implémenter get_converted_coord, get_color, get_id)

        Returns:
            numpy.ndarray: Image modifiée
        """
        position = thing.get_converted_coord()
        color = thing.get_color()
        id = thing.get_id()

        if position is not None:
            x = int(position[0])
            y = int(position[1])

            # Dessin d'un carré représentant l'objet
            cv2.rectangle(frame,
                          (int(position[0] - 2), int(position[1] - 2)),  # Coin sup. gauche
                          (int(position[0] + 2), int(position[1] + 2)),  # Coin inf. droit
                          color,  # Couleur de l'objet
                          -1)  # Remplissage

            # Ajout du texte (ID de l'objet)
            cv2.putText(frame, f"ID: {id}", (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.2,
                        (0, 0, 0), 1)
        return frame

    def draw_keypoints_on_vid(self, frame, keypoints):
        """Dessine des points clés sur la frame (utilisé pour debug).

        Args:
            frame (numpy.ndarray): Image sur laquelle dessiner
            keypoints: Liste de coordonnées de points à dessiner
        """
        for i in range(0, len(keypoints), 2):
            point = (keypoints[i], keypoints[i + 1])
            cv2.circle(frame, point, 3, (255, 255, 255), -1)
            cv2.putText(frame, f"KP: {i // 2}", point,
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 1)

    def update(self, frame, thing):
        """Met à jour la mini-carte en ajoutant un objet.

        Args:
            frame (numpy.ndarray): Image sur laquelle dessiner
            thing: Objet à ajouter à la mini-carte

        Returns:
            numpy.ndarray: Image modifiée
        """
        frame = self.__drawOnMiniMap(frame, thing)
        return frame