import cv2
from utils import bbox_utils as bu, pixel_utils as pu


class Suit:
    def __init__(self, id, bbox, frame, mini_map, keypoints):
        self.suit_id=id
        self.bbox = bbox
        self.color = (0, 0, 255)
        self.converted_coord = self.__get_mapped_point(frame, mini_map, keypoints, draw=False)
        self.lost = False

    def get_converted_coord(self):
        return self.converted_coord

    def get_color(self):
        return self.color

    def get_id(self):
        return self.suit_id

    def __str__(self):
        return f"Suitcase {self.suit_id} at {self.bbox}"

    def __draw_bboxes_stream(self, frame):
        x1, y1, x2, y2 = self.bbox
        #cv2.putText(frame, f"ID: {self.suit_id}", (int(self.bbox[0]), int(self.bbox[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.2,(255, 255, 255), 1)
        if self.lost:
            cv2.putText(frame, f"LOST", (int(self.bbox[0]), int(self.bbox[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0, 0, 255), 1)
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), self.color, 2)

    def drawBBOX(self, frame, lien_dict, pers_pop):
        drawn_bboxes = set()  # Ensemble pour garder une trace des valises déjà dessinées

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
        position = bu.get_center(self.bbox)
        ratioh, ratiov = pu.get_axes_x_y_intersection_ratio(frame, position, keypoints, draw)

        if ratioh is not None and ratiov is not None:
            point = (
                int(mini_map.map_start_x + ratioh * (mini_map.draw_rect_width - 2 * mini_map.padding_map)),
                int(mini_map.map_start_y + ratiov * (mini_map.draw_rect_height - 2 * mini_map.padding_map))
            )
            return point
        return None

    """
    def __drawOnMiniMap(self, frame, pos):

        position = pos['point']
        color = pos['color']
        if position is not None:
            x = int(position[0])
            y = int(position[1])

            

            cv2.rectangle(frame,
                          (int(position[0] - 2), int(position[1] - 2)),  # Point supérieur gauche
                          (int(position[0] + 2), int(position[1] + 2)),  # Point inférieur droit
                          color,  # Couleur (B, G, R)
                          -1)
            #cv2.putText(frame, f"ID: {id}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255, 255, 255), 1)
        return frame"""
