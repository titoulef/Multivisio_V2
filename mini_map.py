import cv2
import sys

import numpy as np

sys.path.append('../')

class MiniMap():
    def __init__(self, frame):
        # map placer en haut à droite par default, voir set_canvas_background_box_position

        self.buffer=20 #marge autour du background
        self.padding_map=10 #marge autour de map dans le backround
        self.draw_rect_width = frame.shape[0] - self.buffer-self.padding_map  # //3
        self.draw_rect_height = frame.shape[1] - self.buffer-self.padding_map # //3

        self.set_canvas_background_box_position(frame)
        self.set_mini_map_position()
        self.set_map_drawing_key_points()
        self.set_map_lines()

        #self.pop=pop

    #set le grand backround rect
    def set_canvas_background_box_position(self, frame):
        frame = frame.copy()
        self.end_x = frame.shape[1] - self.buffer
        self.end_y = self.buffer + self.draw_rect_height
        self.start_x = self.end_x - self.draw_rect_width
        self.start_y = self.end_y - self.draw_rect_height

    #set les keypoints
    def set_map_drawing_key_points(self):
        draw_key_points = [0]*8
        #haut gauche
        draw_key_points[0], draw_key_points[1] = int(self.map_start_x), int(self.map_start_y)
        #haut droite
        draw_key_points[2], draw_key_points[3] = int(self.map_end_x), int(self.map_start_y)
        #bas droite
        draw_key_points[4], draw_key_points[5] = int(self.map_end_x), int(self.map_end_y)
        #bas gauche
        draw_key_points[6], draw_key_points[7] = int(self.map_start_x), int(self.map_end_y)

        self.draw_key_points = draw_key_points

    #set les lignes
    def set_map_lines(self):
        self.lines = {
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0)
        }

    #set la la map
    def set_mini_map_position(self):
        self.map_start_x = self.start_x + self.padding_map
        self.map_start_y = self.start_y + self.padding_map
        self.map_end_x = self.end_x - self.padding_map
        self.map_end_y = self.end_y - self.padding_map
        self.map_drawing_width = self.map_end_x - self.map_start_x

    def draw_map_key(self, frame):
        for i in range(0, len(self.draw_key_points), 2):
            x = int(self.draw_key_points[i])
            y = int(self.draw_key_points[i+1])
            cv2.circle(frame, (x,y), 2, (255, 0, 0), -1)
            cv2.putText(frame, f"KP: {i//2}", (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.2,
                        (255, 255, 255), 1)
        return frame

    def draw_map_lines(self, frame):
        for line in self.lines:
            start_point = (int(self.draw_key_points[line[0]*2]), int(self.draw_key_points[line[0]*2+1]))
            end_point = (int(self.draw_key_points[line[1]*2]), int(self.draw_key_points[line[1]*2 + 1]))
            cv2.line(frame, start_point, end_point, (0, 0, 0), 1)

        return frame

    def draw_backround_rect(self, frame):
        shapes = np.zeros_like(frame, np.uint8)
        #draw rectangle
        cv2.rectangle(shapes, (self.start_x, self.start_y), (self.end_x, self.end_y), (255, 255, 255), cv2.FILLED)
        out = frame.copy()
        alpha=0.5
        mask = shapes.astype(bool)
        out[mask] = cv2.addWeighted(frame, alpha, shapes, 1 - alpha, 0)[mask]
        return out

    #draw la map final
    def draw_mini_map(self, frame):
        frame = self.draw_backround_rect(frame)
        frame = self.draw_map_lines(frame)
        frame = self.draw_map_key(frame)
        return frame


    def __drawOnMiniMap(self, frame, thing):

        position = thing.get_converted_coord()
        color = thing.get_color()
        id = thing.get_id()
        if position is not None:
            x = int(position[0])
            y = int(position[1])

            cv2.rectangle(frame,
                          (int(position[0] - 2), int(position[1] - 2)),  # Point supérieur gauche
                          (int(position[0] + 2), int(position[1] + 2)),  # Point inférieur droit
                          color,  # Couleur (B, G, R)
                          -1)
            cv2.putText(frame, f"ID: {id}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0, 0, 0), 1)
        return frame


    def draw_keypoints_on_vid(self, frame, keypoints):
        for i in range(0, len(keypoints), 2):
            point = (keypoints[i], keypoints[i + 1])
            cv2.circle(frame, point, 3, (255, 255, 255), -1)
            cv2.putText(frame, f"KP: {i // 2}", point, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)



    def update(self, frame, thing):
        frame = self.__drawOnMiniMap(frame, thing)
        return frame