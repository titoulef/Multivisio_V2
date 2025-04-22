import cv2
import numpy as np

from person_package.pers_tracker import PlayerTracker
import suitcase_package as sp
import person_package as pp
from utils import associate_objects, convert_meters_to_pixel_distance
from mini_map import MiniMap
from display.multiViewDisplay import MultiViewDisplay

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Mouse position: ({x}, {y})")


def loop( input_video_path, fpsDivider, videoScale):

    cameraIP = cv2.VideoCapture(input_video_path)
    if not cameraIP.isOpened():
        print("Erreur cam")

    cv2.namedWindow("output")
    cv2.setMouseCallback("output", mouse_callback)
    #fenetre pour la minimap
    cv2.namedWindow("mini_map")
    cpt = 0


    #init
    suit_tracker = sp.SuitcaseTracker(model_path='yolov10n')
    pers_tracker = PlayerTracker(model_path='yolov10n')
    # define keypoints
    #keypoints = [int(k * videoScale) for k in [282, 244, 543, 251, 641, 388, 159, 369]] # hall1
    keypoints = [int(k * videoScale) for k in [275, 205, 545, 205, 640, 335, 180, 320]]  # hall2
    #keypoints = [225, 252, 447, 184, 561, 265, 261, 390]  # hall3

    #keypoints = [int(k * videoScale) for k in [207, 315, 390, 316, 399, 390, 129, 385]]  # hall2

    #keypoints = [int(k * videoScale) for k in [228, 130, 644, 118, 359*2, 398, 2*88, 418]] #cam1

    #photo1 keypoints
    #keypoints = [149, 187, 374, 191, 469, 313, 39, 301]
    #photo2 keypoints
    #keypoints = [2, 273, 137, 116, 326, 117, 416, 274]
    #radius
    radius_in_metter = 1.0
    radius_in_pixel = convert_meters_to_pixel_distance(radius_in_metter, 3, 300-30)
    #
    suit_pop = sp.SuitPop()
    pers_pop = pp.PersPop()

    img = np.ones((300, 300, 3), np.uint8) * 255
    mini_map = MiniMap(img)

    while True:
        ret, frame = cameraIP.read()
        if not ret:
            print("Erreur lecture frame (multivisio.py)")
            break
        if cpt % fpsDivider == 0:
            #resize frame
            frame = cv2.resize(frame, None, fx=float(videoScale), fy=float(videoScale), interpolation=cv2.INTER_CUBIC)
            img = np.ones((300, 300, 3), np.uint8) * 255


            #detect
            suit_pop = suit_tracker.detect_frame(frame, suit_pop, mini_map, keypoints)
            pers_pop = pers_tracker.detect_frame(frame, pers_pop, mini_map, keypoints)

            #associate
            lien_dict = associate_objects(pers_pop, suit_pop, radius_in_pixel)

            #draw keypoints on frame
            mini_map.draw_keypoints_on_vid(frame, keypoints)

            for suit in suit_pop:
                suit.drawBBOX(frame, lien_dict, pers_pop)
                mini_map.update(img, suit)
            for pers in pers_pop:
                pers.drawBBOX(frame)
                mini_map.update(img, pers)

            #generation d'un carré blanc pour la minimap
            cv2.imshow("output", frame)
            cv2.imshow("mini_map", mini_map.draw_mini_map(img))

        cpt += 1
        if cv2.waitKey(1) & 0xff == ord('q'):
            break

        #record video


    cameraIP.release()
    cv2.destroyAllWindows()


def loopRec(input_video_path, fpsDivider, videoScale):
    cameraIP = cv2.VideoCapture(input_video_path)
    if not cameraIP.isOpened():
        print("Erreur cam")

    cv2.namedWindow("output")
    cv2.setMouseCallback("output", mouse_callback)
    # fenetre pour la minimap
    cv2.namedWindow("mini_map")
    cpt = 0

    # Initialisation de l'enregistrement vidéo principale
    frame_width = int(cameraIP.get(cv2.CAP_PROP_FRAME_WIDTH) * videoScale)
    frame_height = int(cameraIP.get(cv2.CAP_PROP_FRAME_HEIGHT) * videoScale)
    output_video_path = 'output_video.avi'
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_video_path, fourcc, 30.0, (frame_width, frame_height))

    # Initialisation de l'enregistrement vidéo pour la minimap
    # La minimap a une taille fixe de 300x300 comme défini dans votre code
    minimap_width = 300
    minimap_height = 300
    output_minimap_path = 'output_maps.avi'
    out2 = cv2.VideoWriter(output_minimap_path, fourcc, 30.0, (minimap_width, minimap_height))

    # init
    suit_tracker = sp.SuitcaseTracker(model_path='yolov10n')
    pers_tracker = PlayerTracker(model_path='yolov10n')
    # define keypoints
    #keypoints = [int(k * videoScale) for k in [282, 244, 543, 251, 641, 388, 159, 369]] # hall1
    #keypoints = [int(k * videoScale) for k in [275, 205, 545, 205, 640, 335, 180, 320]]  # hall2
    keypoints = [int(k * videoScale) for k in [225, 252, 447, 184, 561, 265, 261, 390]]  # hall3
    radius_in_metter = 1.0
    radius_in_pixel = convert_meters_to_pixel_distance(radius_in_metter, 3, 300 - 30)

    suit_pop = sp.SuitPop()
    pers_pop = pp.PersPop()

    img = np.ones((300, 300, 3), np.uint8) * 255
    mini_map = MiniMap(img)

    while True:
        ret, frame = cameraIP.read()
        if not ret:
            print("Erreur lecture frame (multivisio.py)")
            break

        if cpt % fpsDivider == 0:
            # resize frame
            frame = cv2.resize(frame, None, fx=float(videoScale), fy=float(videoScale), interpolation=cv2.INTER_CUBIC)
            img = np.ones((300, 300, 3), np.uint8) * 255

            # detect
            suit_pop = suit_tracker.detect_frame(frame, suit_pop, mini_map, keypoints)
            pers_pop = pers_tracker.detect_frame(frame, pers_pop, mini_map, keypoints)

            # associate
            lien_dict = associate_objects(pers_pop, suit_pop, radius_in_pixel)

            # draw keypoints on frame
            mini_map.draw_keypoints_on_vid(frame, keypoints)

            for suit in suit_pop:
                suit.drawBBOX(frame, lien_dict, pers_pop)
                mini_map.update(img, suit)
            for pers in pers_pop:
                pers.drawBBOX(frame)
                mini_map.update(img, pers)

            # Affichage des fenêtres
            cv2.imshow("output", frame)
            minimap_img = mini_map.draw_mini_map(img)
            cv2.imshow("mini_map", minimap_img)

            # Enregistrement des frames
            out.write(frame)
            out2.write(minimap_img)  # Enregistrement de la minimap

        cpt += 1
        if cv2.waitKey(1) & 0xff == ord('q'):
            break

    # Libération des ressources
    cameraIP.release()
    out.release()  # Fermeture du writer vidéo principale
    out2.release()  # Fermeture du writer vidéo de la minimap
    cv2.destroyAllWindows()

def loop2( input_video_path1, input_video_path2, fpsDivider, videoScale):

    cameraIP1 = cv2.VideoCapture(input_video_path1)
    cameraIP2 = cv2.VideoCapture(input_video_path2)
    if not cameraIP1.isOpened():
        print("Erreur cam1")
    if not cameraIP2.isOpened():
        print("Erreur cam1")

    #fenetre pour la minimap
    cpt = 0
    #init
    suit_tracker1 = sp.SuitcaseTracker(model_path='yolov10n')
    pers_tracker1 = PlayerTracker(model_path='yolov10n')

    suit_tracker2 = sp.SuitcaseTracker(model_path='yolov10n')
    pers_tracker2 = PlayerTracker(model_path='yolov10n')
    # define keypoints
    #keypoints = [282, 244, 543, 251, 641, 388, 159, 369] # hall1
    #keypoints = [275, 205, 545, 205, 640, 335, 180, 320]  # hall2
    #keypoints = [225, 252, 447, 184, 561, 265, 261, 390]  # hall3

    keypoints1 = [int(k*videoScale) for k in [283, 103, 528, 200, 264, 416, 4, 303]] #cam1
    keypoints2 = [int(k*videoScale) for k in [267, 153, 533, 260, 278, 486, 4, 368]] #cam2

    #photo1 keypoints
    #keypoints1 = [149, 187, 374, 191, 469, 313, 39, 301]
    #photo2 keypoints
    #keypoints2 = [2, 273, 137, 116, 326, 117, 416, 274]
    #radius
    radius_in_metter = 1
    radius_in_pixel = convert_meters_to_pixel_distance(radius_in_metter, 3, 300-30)
    #
    lien_dict = {}
    suit_pop1 = sp.SuitPop()
    pers_pop1 = pp.PersPop()
    suit_pop2 = sp.SuitPop()
    pers_pop2 = pp.PersPop()

    img = np.ones((300, 300, 3), np.uint8) * 255
    mini_map1 = MiniMap(img)
    mini_map2 = MiniMap(img)

    # Initialisation
    display = MultiViewDisplay(window_size=(1280, 720), layout="2x2", show_titles=True)
    display.add_view("Vue principale 1")
    display.add_view("Vue principale 2")
    display.add_view("Minimap 1")
    display.add_view("Minimap 2")


    while True:
        ret1, frame1 = cameraIP1.read()
        ret2, frame2 = cameraIP2.read()

        if not ret1:
            print("Erreur lecture frame (multivisio.py)")
            break
        if not ret2:
            print("Erreur lecture frame (multivisio.py)")
            break

        if cpt % fpsDivider == 0:
            #resize frame
            frame1 = cv2.resize(frame1, None, fx=float(videoScale), fy=float(videoScale), interpolation=cv2.INTER_CUBIC)
            frame2 = cv2.resize(frame2, None, fx=float(videoScale), fy=float(videoScale), interpolation=cv2.INTER_CUBIC)
            img1 = np.ones((300, 300, 3), np.uint8) * 255
            img2 = np.ones((300, 300, 3), np.uint8) * 255


            #detect
            suit_pop1 = suit_tracker1.detect_frame(frame1, suit_pop1, mini_map1, keypoints1)
            pers_pop1 = pers_tracker1.detect_frame(frame1, pers_pop1, mini_map1, keypoints1)

            suit_pop2 = suit_tracker2.detect_frame(frame2, suit_pop2, mini_map2, keypoints2)
            pers_pop2 = pers_tracker2.detect_frame(frame2, pers_pop2, mini_map2, keypoints2)

            # lien_dict = TO DO

            #associate
            lien_dict1 = associate_objects(pers_pop1, suit_pop1, radius_in_pixel)
            lien_dict2 = associate_objects(pers_pop2, suit_pop2, radius_in_pixel)

            #lien_dict = TO DO

            # draw keypoints on frame
            mini_map1.draw_keypoints_on_vid(frame1, keypoints1)
            mini_map2.draw_keypoints_on_vid(frame2, keypoints2)

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

                # Affichage
            display.display(frame1, frame2, mini_map1.draw_mini_map(img1), mini_map2.draw_mini_map(img2))
        cpt += 1
        if cv2.waitKey(1) & 0xff == ord('q'):
            break


    cameraIP1.release()
    cameraIP2.release()
    display.close()
    cv2.destroyAllWindows()

