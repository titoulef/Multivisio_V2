import cv2
import numpy as np


class MultiViewDisplay:
    def __init__(self, window_name="Multi-View Display", layout="horizontal", show_titles=True, margin=10):
        """
        Initialise le gestionnaire d'affichage multi-vues.

        Args:
            window_name (str): Nom de la fenêtre
            layout (str): 'horizontal', 'vertical' ou 'grid'
            show_titles (bool): Afficher les titres des vues
            margin (int): Marge entre les frames en pixels
        """
        self.window_name = window_name
        self.layout = layout
        self.show_titles = show_titles
        self.margin = margin
        self.view_titles = []
        self.view_count = 0

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

    def add_view(self, title=""):
        """Ajoute une vue avec un titre optionnel"""
        self.view_titles.append(title)
        self.view_count += 1
        return self.view_count - 1  # Retourne l'index de la vue

    def display(self, *frames):
        """
        Affiche les frames selon la configuration choisie.

        Args:
            *frames: Liste des frames à afficher (peut inclure None pour les vues vides)
        """
        if len(frames) != self.view_count:
            raise ValueError(
                f"Nombre de frames ({len(frames)}) ne correspond pas au nombre de vues ({self.view_count})")

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

        # Redimensionner toutes les frames à la même taille (celle de la première frame)
        target_h, target_w = processed_frames[0].shape[:2]
        resized_frames = []
        for frame in processed_frames:
            if frame.shape[0] != target_h or frame.shape[1] != target_w:
                frame = cv2.resize(frame, (target_w, target_h))
            resized_frames.append(frame)

        # Créer la vue combinée selon le layout
        if self.layout == "horizontal":
            combined = self._combine_horizontally(resized_frames)
        elif self.layout == "vertical":
            combined = self._combine_vertically(resized_frames)
        elif self.layout == "grid":
            combined = self._combine_grid(resized_frames)
        else:
            raise ValueError("Layout non supporté. Choisir 'horizontal', 'vertical' ou 'grid'")

        cv2.imshow(self.window_name, combined)

    def _add_title(self, frame, title):
        """Ajoute un titre à une frame"""
        frame = frame.copy()
        cv2.putText(frame, title, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return frame

    def _combine_horizontally(self, frames):
        """Combine les frames horizontalement avec une marge"""
        # Ajouter une marge à droite de chaque frame sauf la dernière
        frames_with_margin = []
        for i, frame in enumerate(frames[:-1]):
            margin = np.zeros((frame.shape[0], self.margin, 3), dtype=np.uint8)
            frames_with_margin.append(np.hstack([frame, margin]))
        frames_with_margin.append(frames[-1])

        return np.hstack(frames_with_margin)

    def _combine_vertically(self, frames):
        """Combine les frames verticalement avec une marge"""
        # Ajouter une marge en bas de chaque frame sauf la dernière
        frames_with_margin = []
        for i, frame in enumerate(frames[:-1]):
            margin = np.zeros((self.margin, frame.shape[1], 3), dtype=np.uint8)
            frames_with_margin.append(np.vstack([frame, margin]))
        frames_with_margin.append(frames[-1])

        return np.vstack(frames_with_margin)

    def _combine_grid(self, frames):
        """Combine les frames en une grille carrée"""
        rows = int(np.ceil(np.sqrt(self.view_count)))
        cols = int(np.ceil(self.view_count / rows))

        # Créer une grille vide
        grid = []
        for r in range(rows):
            row_frames = []
            for c in range(cols):
                idx = r * cols + c
                if idx < len(frames):
                    frame = frames[idx]
                else:
                    frame = np.zeros_like(frames[0])

                # Ajouter une marge à droite sauf pour la dernière colonne
                if c < cols - 1:
                    margin = np.zeros((frame.shape[0], self.margin, 3), dtype=np.uint8)
                    frame = np.hstack([frame, margin])

                row_frames.append(frame)

            # Combiner la ligne
            row_combined = np.hstack(row_frames)

            # Ajouter une marge en bas sauf pour la dernière ligne
            if r < rows - 1:
                margin = np.zeros((self.margin, row_combined.shape[1], 3), dtype=np.uint8)
                row_combined = np.vstack([row_combined, margin])

            grid.append(row_combined)

        return np.vstack(grid)

    def close(self):
        """Ferme la fenêtre"""
        cv2.destroyWindow(self.window_name)