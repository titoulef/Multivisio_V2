# Importation des bibliothèques nécessaires
from ultralytics import YOLO  # Importation du modèle YOLO pour la détection d'objets
import pandas as pd  # Importation de pandas pour la manipulation des données
import numpy as np  # Importation de numpy pour les opérations numériques
from deep_sort.deep_sort import DeepSort  # Importation de DeepSort pour le suivi d'objets
import suitcase_package as sp  # Importation du package pour la gestion des valises

# Chemin vers les poids du modèle DeepSort
DEEP_SORT_WEIGHTS = 'C:/Ensta/Tracking/wetransfer_deep_sort_2025-02-04_1256/deep_sort/deep/checkpoint/ckpt.t7'

class SuitcaseTracker:
    def __init__(self, model_path):
        """
        Initialise une nouvelle instance de la classe SuitcaseTracker.

        :param model_path: Chemin vers le modèle YOLO pour la détection d'objets.
        """
        self.model = YOLO(model_path)  # Chargement du modèle YOLO
        self.tracker = DeepSort(model_path=DEEP_SORT_WEIGHTS, max_age=30)  # Initialisation du tracker DeepSort
        self.historical_positions = pd.DataFrame(columns=['x1', 'y1', 'x2', 'y2'])  # DataFrame pour stocker les positions historiques
        self.frames = []  # Liste pour stocker les trames vidéo

    def detect_frame(self, frame, suit_pop, mini_map, keypoints):
        """
        Détecte les valises dans une trame vidéo et met à jour la population de valises.

        :param frame: Trame vidéo actuelle.
        :param suit_pop: Objet SuitPop pour gérer la collection de valises.
        :param mini_map: Carte miniature pour le suivi.
        :param keypoints: Points clés pour le mappage des coordonnées.
        :return: Objet SuitPop mis à jour avec les valises détectées.
        """
        suit_pop.clear()  # Vide la collection de valises actuelle

        # Détection des objets dans la trame avec le modèle YOLO
        results = self.model(frame, classes=[28], conf=0.1, verbose=False)

        # Conversion des résultats en détections (boîtes englobantes, confiance, classe)
        detections = [
            (
                [int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2), int(box[2] - box[0]), int(box[3] - box[1])],
                float(box[4]),
                int(box[5])
            )
            for box in results[0].boxes.data.tolist()
        ]

        if detections:
            # Conversion des boîtes englobantes au format xywh
            bboxes_xywh = np.array([det[0] for det in detections], dtype=float)
            confidences = np.array([det[1] for det in detections], dtype=float)

            # Mise à jour du tracker DeepSort avec les nouvelles détections
            tracks = self.tracker.update(bboxes_xywh, confidences, frame)

            # Ajout des valises détectées à la collection
            for track in tracks:
                track_id = int(track[4])  # Identifiant unique du track
                x1, y1, x2, y2 = map(int, track[:4])  # Coordonnées de la boîte englobante

                # Ajout de la valise à la collection
                suit_pop.add(sp.Suit(id=track_id, bbox=[x1, y1, x2, y2], frame=frame, mini_map=mini_map, keypoints=keypoints))

        return suit_pop  # Retourne la collection de valises mise à jour
