from ultralytics import YOLO
import cv2
import numpy as np
from deep_sort.deep_sort import DeepSort
import person_package as pp

DEEP_SORT_WEIGHTS = 'C:/Ensta/Tracking/wetransfer_deep_sort_2025-02-04_1256/deep_sort/deep/checkpoint/ckpt.t7'


class PlayerTracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.tracker = DeepSort(model_path=DEEP_SORT_WEIGHTS, max_age=30)
        self.colors = {}

    def generate_color(self):
        return tuple(np.random.randint(0, 255, size=3).tolist())

    def detect_frame(self, frame, pers_pop, mini_map, keypoints):
        pers_pop.clear()
        results = self.model(frame, classes=[0], conf=0.5, verbose=False)
        detections = [([int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2), int(box[2] - box[0]),
                        int(box[3] - box[1])], float(box[4]), int(box[5])) for box in results[0].boxes.data.tolist()]

        if detections:
            bboxes_xywh = np.array([det[0] for det in detections], dtype=float)
            confidences = np.array([det[1] for det in detections], dtype=float)
            tracks = self.tracker.update(bboxes_xywh, confidences, frame)

            for track in tracks:
                track_id = int(track[4])
                x1, y1, x2, y2 = map(int, track[:4])
                if track_id not in self.colors:
                    self.colors[track_id] = self.generate_color()

                # Créer une instance de Person
                pers_pop.add(pp.Person(id=track_id, bbox=[x1, y1, x2, y2], frame=frame, mini_map=mini_map, keypoints=keypoints))

        return pers_pop