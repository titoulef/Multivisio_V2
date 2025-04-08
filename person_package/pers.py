import cv2
from utils import bbox_utils as bu, pixel_utils as pu
import numpy as np
import time

class Person:
    def __init__(self, id, bbox, frame, mini_map, keypoints):
        self.hum_id=id
        self.bbox = bbox
        self.color = self.__generate_color()
        self.converted_coord = self.__get_mapped_point(frame, mini_map, keypoints, draw=False)

    def get_converted_coord(self):
        return self.converted_coord

    def get_color(self):
        return self.color

    def get_id(self):
        return self.hum_id


    def __generate_color(self):
        return tuple(np.random.randint(0, 255, size=3).tolist())

    def __str__(self):
        return f"Pers {self.hum_id} at {self.bbox} with color {self.color}"

    def __draw_bboxes_stream(self, frame):
        x1, y1, x2, y2 = self.bbox
        cv2.putText(frame, f"ID: {self.hum_id}", (int(self.bbox[0]), int(self.bbox[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.2,
                    (255, 255, 255), 1)

        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), self.color, 2)

    def drawBBOX(self, frame):
        drawn_player_bboxes = set()
        if self.hum_id not in drawn_player_bboxes:
            self.__draw_bboxes_stream(frame)
            drawn_player_bboxes.add(self.hum_id)


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


    def __drawOnMiniMap(self, frame, pos):

        position = pos['point']
        color = pos['color']
        if position is not None:
            x = int(position[0])
            y = int(position[1])

            """if x < self.map_start_x - self.padding_map:
                position = (self.map_start_x - self.padding_map, y)
            if x > self.map_end_x + self.padding_map:
                position = (self.map_end_x + self.padding_map, y)
            if y < self.map_start_y - self.padding_map:
                position = (x, self.map_start_y - self.padding_map)
            if y > self.map_end_y + self.padding_map:
                position = (x, self.map_end_y + self.padding_map)"""

            cv2.rectangle(frame,
                          (int(position[0] - 2), int(position[1] - 2)),  # Point supérieur gauche
                          (int(position[0] + 2), int(position[1] + 2)),  # Point inférieur droit
                          color,  # Couleur (B, G, R)
                          -1)
            #cv2.putText(frame, f"ID: {id}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255, 255, 255), 1)
        return frame




