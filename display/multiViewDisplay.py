import cv2
import numpy as np


class MultiViewDisplay:
    def __init__(self, window_name="Multi-View Display", layout="2x2", show_titles=True, margin=10,
                 window_size=(1280, 720)):
        """
        Initialise le gestionnaire d'affichage multi-vues.

        Args:
            window_name (str): Nom de la fenêtre
            layout (str): '2x2' pour deux vidéos en haut et deux minimaps en dessous
            show_titles (bool): Afficher les titres des vues
            margin (int): Marge entre les frames en pixels
            window_size (tuple): Taille initiale de la fenêtre (largeur, hauteur)
        """
        self.window_name = window_name
        self.layout = layout
        self.show_titles = show_titles
        self.margin = margin
        self.window_size = window_size  # (width, height)
        self.view_titles = []
        self.view_count = 0

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.window_size[0], self.window_size[1])

    def add_view(self, title=""):
        """Ajoute une vue avec un titre optionnel"""
        self.view_titles.append(title)
        self.view_count += 1
        return self.view_count - 1  # Retourne l'index de la vue

    def display(self, *frames):
        """
        Affiche les frames selon la configuration choisie.

        Args:
            *frames: Liste des frames à afficher (doit contenir 4 frames: vidéo1, vidéo2, minimap1, minimap2)
        """
        if len(frames) != 4:
            raise ValueError(
                f"Nombre de frames ({len(frames)}) doit être 4 (vidéo1, vidéo2, minimap1, minimap2)")

        # Prétraiter chaque frame
        processed_frames = []
        for i, frame in enumerate(frames):
            if frame is None:
                # Créer une frame vide si None est fourni
                if processed_frames:
                    h, w = processed_frames[0].shape[:2]
                    frame = np.zeros((h, w, 3), dtype=np.uint8)
                else:
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)

            # Ajouter le titre si configuré
            if self.show_titles and i < len(self.view_titles):
                frame = self._add_title(frame, self.view_titles[i])

            processed_frames.append(frame)

        # Redimensionner les frames pour qu'elles aient toutes la même largeur
        max_width = max(frame.shape[1] for frame in processed_frames[:2])  # Largeur max des vidéos principales
        minimap_width = max(frame.shape[1] for frame in processed_frames[2:])  # Largeur max des minimaps

        # Redimensionner les frames principales
        resized_main_frames = []
        for frame in processed_frames[:2]:
            if frame.shape[1] != max_width:
                scale = max_width / frame.shape[1]
                new_height = int(frame.shape[0] * scale)
                frame = cv2.resize(frame, (max_width, new_height))
            resized_main_frames.append(frame)

        # Redimensionner les minimaps
        resized_minimaps = []
        for frame in processed_frames[2:]:
            if frame.shape[1] != minimap_width:
                scale = minimap_width / frame.shape[1]
                new_height = int(frame.shape[0] * scale)
                frame = cv2.resize(frame, (minimap_width, new_height))
            resized_minimaps.append(frame)

        # Ajuster la largeur des minimaps pour qu'elle corresponde à celle des vidéos principales
        if resized_main_frames and resized_minimaps:
            total_main_width = sum(f.shape[1] for f in resized_main_frames) + self.margin * (
                        len(resized_main_frames) - 1)
            total_minimap_width = sum(f.shape[1] for f in resized_minimaps) + self.margin * (len(resized_minimaps) - 1)

            # Si les largeurs totales sont différentes, redimensionner les minimaps
            if total_main_width != total_minimap_width:
                scale = total_main_width / total_minimap_width
                for i in range(len(resized_minimaps)):
                    new_w = int(resized_minimaps[i].shape[1] * scale)
                    new_h = int(resized_minimaps[i].shape[0] * scale)
                    resized_minimaps[i] = cv2.resize(resized_minimaps[i], (new_w, new_h))

        # Créer la vue combinée en disposition 2x2
        if self.layout == "2x2":
            # Combiner les frames principales horizontalement
            main_row = self._combine_horizontally(resized_main_frames)

            # Combiner les minimaps horizontalement
            minimap_row = self._combine_horizontally(resized_minimaps)

            # Vérifier que les deux lignes ont la même largeur
            if main_row.shape[1] != minimap_row.shape[1]:
                # Ajuster la hauteur pour conserver le ratio
                new_width = main_row.shape[1]
                new_height = int(minimap_row.shape[0] * (new_width / minimap_row.shape[1]))
                minimap_row = cv2.resize(minimap_row, (new_width, new_height))

            # Combiner les deux lignes verticalement
            combined = self._combine_vertically([main_row, minimap_row])
        else:
            raise ValueError("Layout non supporté. Utiliser '2x2'")

        cv2.imshow(self.window_name, combined)
        # Maintenir la taille de la fenêtre
        cv2.resizeWindow(self.window_name, self.window_size[0], self.window_size[1])

    def _add_title(self, frame, title):
        """Ajoute un titre à une frame"""
        frame = frame.copy()
        cv2.putText(frame, title, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return frame

    def _combine_horizontally(self, frames):
        """Combine les frames horizontalement avec une marge"""
        if not frames:
            return np.zeros((480, 640, 3), dtype=np.uint8)

        # Ajouter une marge à droite de chaque frame sauf la dernière
        frames_with_margin = []
        for i, frame in enumerate(frames[:-1]):
            margin = np.zeros((frame.shape[0], self.margin, 3), dtype=np.uint8)
            frames_with_margin.append(np.hstack([frame, margin]))
        frames_with_margin.append(frames[-1])

        return np.hstack(frames_with_margin)

    def _combine_vertically(self, frames):
        """Combine les frames verticalement avec une marge"""
        if not frames:
            return np.zeros((480, 640, 3), dtype=np.uint8)

        # Ajuster toutes les frames à la même largeur (la plus grande)
        max_width = max(frame.shape[1] for frame in frames)
        adjusted_frames = []
        for frame in frames:
            if frame.shape[1] != max_width:
                # Conserver le ratio d'aspect
                new_height = int(frame.shape[0] * (max_width / frame.shape[1]))
                frame = cv2.resize(frame, (max_width, new_height))
            adjusted_frames.append(frame)

        # Ajouter une marge en bas de chaque frame sauf la dernière
        frames_with_margin = []
        for i, frame in enumerate(adjusted_frames[:-1]):
            margin = np.zeros((self.margin, frame.shape[1], 3), dtype=np.uint8)
            frames_with_margin.append(np.vstack([frame, margin]))
        frames_with_margin.append(adjusted_frames[-1])

        return np.vstack(frames_with_margin)

    def close(self):
        """Ferme la fenêtre"""
        cv2.destroyWindow(self.window_name)