# Importation des bibliothèques nécessaires
import cv2  # Bibliothèque OpenCV pour le traitement d'images et de vidéos
import numpy as np  # Bibliothèque pour les opérations numériques

# Importation des modules personnalisés
from person_package.pers_tracker import PlayerTracker  # Importation du tracker de joueurs
import suitcase_package as sp  # Importation du package pour la gestion des valises
import person_package as pp  # Importation du package pour la gestion des personnes
from utils import associate_objects, convert_meters_to_pixel_distance  # Importation des utilitaires pour l'association et la conversion de distances
from mini_map import MiniMap  # Importation de la classe pour la gestion de la mini-carte
from display.multiViewDisplay import MultiViewDisplay  # Importation de la classe pour l'affichage multi-vues

def mouse_callback(event, x, y, flags, param):
    """
    Callback pour gérer les événements de souris.

    :param event: Type d'événement de la souris.
    :param x: Coordonnée x de la souris.
    :param y: Coordonnée y de la souris.
    :param flags: Flags de l'événement.
    :param param: Paramètres supplémentaires.
    """
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Mouse position: ({x}, {y})")

def loop(input_video_path, keypoints, fpsDivider, videoScale):
    """
    Boucle principale de traitement pour une seule caméra.

    :param input_video_path: Chemin vers la vidéo d'entrée.
    :param keypoints: Points clés pour la transformation perspective.
    :param fpsDivider: Diviseur pour réduire le taux de traitement.
    :param videoScale: Facteur de mise à l'échelle de la vidéo.
    """
    # Initialisation de la capture vidéo
    cameraIP = cv2.VideoCapture(input_video_path)
    if not cameraIP.isOpened():
        print("Erreur cam")

    # Création des fenêtres d'affichage
    cv2.namedWindow("output")
    cv2.setMouseCallback("output", mouse_callback)
    cv2.namedWindow("mini_map")
    cpt = 0  # Compteur de frames

    # Initialisation des trackers
    suit_tracker = sp.SuitcaseTracker(model_path='yolov10n')
    pers_tracker = PlayerTracker(model_path='yolov10n')

    # Configuration du rayon d'association
    radius_in_metter = 1.0
    radius_in_pixel = convert_meters_to_pixel_distance(radius_in_metter, 3, 300 - 30)

    # Initialisation des populations d'objets
    suit_pop = sp.SuitPop()
    pers_pop = pp.PersPop()

    # Initialisation de la mini-carte
    img = np.ones((300, 300, 3), np.uint8) * 255
    mini_map = MiniMap(img)

    while True:
        # Lecture de la frame
        ret, frame = cameraIP.read()
        if not ret:
            print("Erreur lecture frame (multivisio.py)")
            break

        # Traitement à intervalle régulier (selon fpsDivider)
        if cpt % fpsDivider == 0:
            # Redimensionnement de la frame
            frame = cv2.resize(frame, None, fx=float(videoScale), fy=float(videoScale),
                               interpolation=cv2.INTER_CUBIC)
            img = np.ones((300, 300, 3), np.uint8) * 255

            # Détection des valises et personnes
            suit_pop = suit_tracker.detect_frame(frame, suit_pop, mini_map, keypoints)
            pers_pop = pers_tracker.detect_frame(frame, pers_pop, mini_map, keypoints)

            # Association personnes-valises
            lien_dict = associate_objects(pers_pop, suit_pop, radius_in_pixel)

            # Affichage des points clés
            mini_map.draw_keypoints_on_vid(frame, keypoints)

            # Dessin des boîtes englobantes et mise à jour de la mini-carte
            for suit in suit_pop:
                suit.drawBBOX(frame, lien_dict, pers_pop)
                mini_map.update(img, suit)

            for pers in pers_pop:
                pers.drawBBOX(frame)
                mini_map.update(img, pers)

            # Affichage des résultats
            cv2.imshow("output", frame)
            cv2.imshow("mini_map", mini_map.draw_mini_map(img))

        cpt += 1
        # Sortie si 'q' est pressé
        if cv2.waitKey(1) & 0xff == ord('q'):
            break

    # Nettoyage
    cameraIP.release()
    cv2.destroyAllWindows()

def loop2(input_video_path1, input_video_path2, keypoints1, keypoints2, fpsDivider, videoScale):
    """
    Boucle principale de traitement pour deux caméras.

    :param input_video_path1: Chemin vers la première vidéo.
    :param input_video_path2: Chemin vers la deuxième vidéo.
    :param keypoints1: Points clés pour la caméra 1.
    :param keypoints2: Points clés pour la caméra 2.
    :param fpsDivider: Diviseur pour réduire le taux de traitement.
    :param videoScale: Facteur de mise à l'échelle de la vidéo.
    """
    # Initialisation des captures vidéo
    cameraIP1 = cv2.VideoCapture(input_video_path1)
    cameraIP2 = cv2.VideoCapture(input_video_path2)
    if not cameraIP1.isOpened():
        print("Erreur cam1")
    if not cameraIP2.isOpened():
        print("Erreur cam2")

    cpt = 0  # Compteur de frames

    # Initialisation des trackers pour les deux caméras
    suit_tracker1 = sp.SuitcaseTracker(model_path='yolov10n')
    pers_tracker1 = PlayerTracker(model_path='yolov10n')
    suit_tracker2 = sp.SuitcaseTracker(model_path='yolov10n')
    pers_tracker2 = PlayerTracker(model_path='yolov10n')

    # Configuration du rayon d'association
    radius_in_metter = 1
    cote_carre_in_metter = 3
    radius_in_pixel = convert_meters_to_pixel_distance(radius_in_metter, cote_carre_in_metter, 300 - 30)

    # Initialisation des populations d'objets
    suit_pop1 = sp.SuitPop()
    pers_pop1 = pp.PersPop()
    suit_pop2 = sp.SuitPop()
    pers_pop2 = pp.PersPop()

    # Initialisation des mini-cartes
    img = np.ones((300, 300, 3), np.uint8) * 255
    mini_map1 = MiniMap(img)
    mini_map2 = MiniMap(img)

    # Initialisation de l'affichage multi-vues
    display = MultiViewDisplay(window_size=(720, 720), layout="2x2", show_titles=True)
    display.add_view("Vue principale 1")
    display.add_view("Vue principale 2")
    display.add_view("Minimap 1")
    display.add_view("Minimap 2")

    while True:
        # Lecture des frames
        ret1, frame1 = cameraIP1.read()
        ret2, frame2 = cameraIP2.read()

        if not ret1 or not ret2:
            print("Erreur lecture frame (multivisio.py)")
            break

        # Traitement à intervalle régulier
        if cpt % fpsDivider == 0:
            # Redimensionnement des frames
            frame1 = cv2.resize(frame1, None, fx=float(videoScale), fy=float(videoScale),
                                interpolation=cv2.INTER_CUBIC)
            frame2 = cv2.resize(frame2, None, fx=float(videoScale), fy=float(videoScale),
                                interpolation=cv2.INTER_CUBIC)

            img1 = np.ones((300, 300, 3), np.uint8) * 255
            img2 = np.ones((300, 300, 3), np.uint8) * 255

            # Détection des objets dans les deux caméras
            suit_pop1 = suit_tracker1.detect_frame(frame1, suit_pop1, mini_map1, keypoints1)
            pers_pop1 = pers_tracker1.detect_frame(frame1, pers_pop1, mini_map1, keypoints1)
            suit_pop2 = suit_tracker2.detect_frame(frame2, suit_pop2, mini_map2, keypoints2)
            pers_pop2 = pers_tracker2.detect_frame(frame2, pers_pop2, mini_map2, keypoints2)

            # Association personnes-valises
            lien_dict1 = associate_objects(pers_pop1, suit_pop1, radius_in_pixel)
            lien_dict2 = associate_objects(pers_pop2, suit_pop2, radius_in_pixel)

            # Affichage des points clés
            mini_map1.draw_keypoints_on_vid(frame1, keypoints1)
            mini_map2.draw_keypoints_on_vid(frame2, keypoints2)

            # Dessin des boîtes englobantes et mise à jour des mini-cartes
            for suit in suit_pop1:
                suit.drawBBOX(frame1, lien_dict1, pers_pop1)
                mini_map1.update(img1, suit)

            for suit in suit_pop2:
                suit.drawBBOX(frame2, lien_dict2, pers_pop2)
                mini_map2.update(img2, suit)

            for pers in pers_pop1:
                pers.drawBBOX(frame1)
                mini_map1.update(img1, pers)

            for pers in pers_pop2:
                pers.drawBBOX(frame2)
                mini_map2.update(img2, pers)

            # Affichage des résultats
            display.display(frame1, frame2, mini_map1.draw_mini_map(img1), mini_map2.draw_mini_map(img2))

        cpt += 1
        # Sortie si 'q' est pressé
        if cv2.waitKey(1) & 0xff == ord('q'):
            break

    # Nettoyage
    cameraIP1.release()
    cameraIP2.release()
    display.close()
    cv2.destroyAllWindows()

def loop2_masked(input_video_path1, input_video_path2, keypoints1, keypoints2, fpsDivider, videoScale):
    """
    Version masquée de la boucle à deux caméras (simplifiée).

    :param input_video_path1: Chemin vers la première vidéo.
    :param input_video_path2: Chemin vers la deuxième vidéo.
    :param keypoints1: Points clés pour la caméra 1.
    :param keypoints2: Points clés pour la caméra 2.
    :param fpsDivider: Diviseur pour réduire le taux de traitement.
    :param videoScale: Facteur de mise à l'échelle de la vidéo.
    """
    # Initialisation similaire à loop2 mais avec une seule mini-carte
    cameraIP1 = cv2.VideoCapture(input_video_path1)
    cameraIP2 = cv2.VideoCapture(input_video_path2)
    if not cameraIP1.isOpened():
        print("Erreur cam1")
    if not cameraIP2.isOpened():
        print("Erreur cam2")

    cpt = 0
    # Initialisation des trackers
    suit_tracker1 = sp.SuitcaseTracker(model_path='yolov10n')
    pers_tracker1 = PlayerTracker(model_path='yolov10n')
    suit_tracker2 = sp.SuitcaseTracker(model_path='yolov10n')
    pers_tracker2 = PlayerTracker(model_path='yolov10n')

    # Configuration du rayon d'association
    radius_in_metter = 1
    radius_in_pixel = convert_meters_to_pixel_distance(radius_in_metter, 3, 300 - 30)

    # Initialisation des populations d'objets
    suit_pop1 = sp.SuitPop()
    pers_pop1 = pp.PersPop()
    suit_pop2 = sp.SuitPop()
    pers_pop2 = pp.PersPop()

    # Initialisation d'une seule mini-carte
    img = np.ones((300, 300, 3), np.uint8) * 255
    mini_map = MiniMap(img)

    # Configuration de l'affichage
    display = MultiViewDisplay(window_size=(720, 720), layout="2x2", show_titles=True)
    display.add_view("Vue principale 1")
    display.add_view("Vue principale 2")
    display.add_view("Minimap")

    while True:
        # Lecture des frames
        ret1, frame1 = cameraIP1.read()
        ret2, frame2 = cameraIP2.read()

        if not ret1 or not ret2:
            print("Erreur lecture frame (multivisio.py)")
            break

        if cpt % fpsDivider == 0:
            # Redimensionnement des frames
            frame1 = cv2.resize(frame1, None, fx=float(videoScale), fy=float(videoScale),
                                interpolation=cv2.INTER_CUBIC)
            frame2 = cv2.resize(frame2, None, fx=float(videoScale), fy=float(videoScale),
                                interpolation=cv2.INTER_CUBIC)
            img1 = np.ones((300, 300, 3), np.uint8) * 255

            # Détection des objets
            suit_pop1 = suit_tracker1.detect_frame(frame1, suit_pop1, mini_map, keypoints1)
            pers_pop1 = pers_tracker1.detect_frame(frame1, pers_pop1, mini_map, keypoints1)
            suit_pop2 = suit_tracker2.detect_frame(frame2, suit_pop2, mini_map, keypoints2)
            pers_pop2 = pers_tracker2.detect_frame(frame2, pers_pop2, mini_map, keypoints2)

            # Association personnes-valises
            lien_dict1 = associate_objects(pers_pop1, suit_pop1, radius_in_pixel)
            lien_dict2 = associate_objects(pers_pop2, suit_pop2, radius_in_pixel)

            # Affichage des points clés
            mini_map.draw_keypoints_on_vid(frame1, keypoints1)
            mini_map.draw_keypoints_on_vid(frame2, keypoints2)

            # Dessin des boîtes englobantes et mise à jour de la mini-carte
            for suit in suit_pop1:
                suit.drawBBOX(frame1, lien_dict1, pers_pop1)
                mini_map.update(img1, suit)

            for suit in suit_pop2:
                suit.drawBBOX(frame2, lien_dict2, pers_pop2)
                mini_map.update(img1, suit)

            for pers in pers_pop1:
                pers.drawBBOX(frame1)
                mini_map.update(img1, pers)

            for pers in pers_pop2:
                pers.drawBBOX(frame2)
                mini_map.update(img1, pers)

            # Affichage des résultats
            display.display(frame1, frame2, mini_map.draw_mini_map(img1), mini_map.draw_mini_map(img1))

        cpt += 1
        # Sortie si 'q' est pressé
        if cv2.waitKey(1) & 0xff == ord('q'):
            break

    # Nettoyage
    cameraIP1.release()
    cameraIP2.release()
    display.close()
    cv2.destroyAllWindows()
