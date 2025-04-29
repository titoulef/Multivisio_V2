from ultralytics import YOLO  # Importation du modèle YOLO pour la détection d'objets
import cv2  # Importation d'OpenCV pour le traitement d'image
import numpy as np  # Importation de NumPy pour les opérations numériques
from deep_sort.deep_sort import DeepSort  # Importation de DeepSort pour le suivi d'objets
import person_package as pp  # Importation du package personnalisé pour la gestion des personnes

# Chemin vers les poids du modèle DeepSort
DEEP_SORT_WEIGHTS = 'C:/Ensta/Tracking/wetransfer_deep_sort_2025-02-04_1256/deep_sort/deep/checkpoint/ckpt.t7'

class PlayerTracker:
    def __init__(self, model_path):
        """
        Initialise une nouvelle instance de la classe PlayerTracker.

        :param model_path: Chemin vers le modèle YOLO
        """
        self.model = YOLO(model_path)  # Charge le modèle YOLO
        self.tracker = DeepSort(model_path=DEEP_SORT_WEIGHTS, max_age=30)  # Initialise DeepSort avec les poids spécifiés
        self.colors = {}  # Dictionnaire pour stocker les couleurs associées aux IDs des personnes

    def generate_color(self):
        """
        Génère une couleur aléatoire.

        :return: Couleur sous forme de tuple (R, G, B)
        """
        return tuple(np.random.randint(0, 255, size=3).tolist())

    def detect_frame(self, frame, pers_pop, mini_map, keypoints):
        """
        Détecte et suit les personnes dans une trame vidéo.

        :param frame: Trame vidéo actuelle
        :param pers_pop: Instance de PersPop pour gérer la population de personnes
        :param mini_map: Carte miniature pour le suivi
        :param keypoints: Points clés pour le mappage
        :return: Instance de PersPop mise à jour avec les personnes détectées
        """
        pers_pop.clear()  # Vide la population actuelle de personnes

        # Effectue la détection avec le modèle YOLO
        results = self.model(frame, classes=[0], conf=0.5, verbose=False)

        # Convertit les résultats en détections utilisables par DeepSort
        detections = [
            ([int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2), int(box[2] - box[0]), int(box[3] - box[1])],
             float(box[4]), int(box[5]))
            for box in results[0].boxes.data.tolist()
        ]

        if detections:
            # Prépare les boîtes englobantes et les confiances pour DeepSort
            bboxes_xywh = np.array([det[0] for det in detections], dtype=float)
            confidences = np.array([det[1] for det in detections], dtype=float)

            # Met à jour les pistes avec DeepSort
            tracks = self.tracker.update(bboxes_xywh, confidences, frame)

            for track in tracks:
                track_id = int(track[4])  # Récupère l'ID de la piste
                x1, y1, x2, y2 = map(int, track[:4])  # Récupère les coordonnées de la boîte englobante

                # Génère une couleur si l'ID n'en a pas encore une
                if track_id not in self.colors:
                    self.colors[track_id] = self.generate_color()

                # Crée une instance de Person et l'ajoute à la population
                pers_pop.add(pp.Person(id=track_id, bbox=[x1, y1, x2, y2], frame=frame, mini_map=mini_map, keypoints=keypoints))

        return pers_pop  # Retourne la population mise à jour
