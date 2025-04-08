import numpy as np
import cv2

def convert_pixels_to_meters(pixels_dist, reference_height_in_meters, reference_height_in_pixels):
    return pixels_dist * reference_height_in_meters / reference_height_in_pixels

def convert_meters_to_pixel_distance(meters, reference_height_in_meters, reference_height_in_pixels):
    return meters * reference_height_in_pixels / reference_height_in_meters

def normalize(v):
    x,y=v
    v=np.array([x,y])
    norm = np.linalg.norm(v)
    if norm == 0:
       return v
    nomalize =v / norm
    x,y=nomalize
    return (x,y)

def get_angle_from_x(segment):
    x, y = segment
    return np.arctan(y/x)

def get_angle_from_y(segment):
    x, y = segment
    return np.arctan(x/y)

def detect_intersection_seg_vect(vector_origin, vector_direction, segment_start, segment_end):
    """
    Détecte l'intersection entre un vecteur et un segment.

    :param vector_origin: Coordonnées d'origine du vecteur (x, y).
    :param vector_direction: Direction du vecteur (dx, dy).
    :param segment_start: Coordonnées du premier point du segment (x, y).
    :param segment_end: Coordonnées du second point du segment (x, y).
    :return: Coordonnées de l'intersection (x, y) ou None s'il n'y a pas d'intersection.
    """
    # Convertir les points en numpy arrays pour simplifier les calculs
    p = np.array(vector_origin)
    d = np.array(vector_direction)
    a = np.array(segment_start)
    b = np.array(segment_end)

    # Calcul des vecteurs pour le segment
    ab = b - a
    ap = p - a

    return intersection_droites_parametriques(p, d, a, ab)

def get_segs(keypoints):
    seg01 = (keypoints[2] - keypoints[0], keypoints[3] - keypoints[1])
    seg12 = (keypoints[4] - keypoints[2], keypoints[5] - keypoints[3])
    seg32 = (keypoints[4] - keypoints[6], keypoints[5] - keypoints[7])
    seg03 = (keypoints[6] - keypoints[0], keypoints[7] - keypoints[1])
    segs = [seg01, seg12, seg32, seg03]
    return segs

def norms(vect):
    x,y=vect
    return (x**2 + y**2)**0.5

def get_segs_norms(keypoints):
    up, right, down, left = get_segs(keypoints)
    up=norms(up)
    right=norms(right)
    down=norms(down)
    left=norms(left)
    return up, right, down, left

def get_distance_from_origin(origin, p2):
    x1, y1 = origin
    x2, y2 = p2
    return np.sqrt((x2-x1)**2 + (y2-y1)**2)

def get_axes_x_y(keypoints):
    segs=get_segs(keypoints)
    theta_down = get_angle_from_x(segs[2])
    theta_up = get_angle_from_x(segs[0])
    phi_left = get_angle_from_y(segs[3])
    phi_right = get_angle_from_y(segs[1])
    theta = np.mean([theta_down, theta_up])
    phi = np.mean([phi_left, phi_right])
    dirx = (np.cos(theta), np.sin(theta))
    diry = (np.sin(phi), np.cos(phi))
    return dirx, diry

def get_axes_direct(keypoints):
    segs=get_segs(keypoints)
    theta_down = get_angle_from_x(segs[2])
    theta_up = get_angle_from_x(segs[0])
    phi_left = get_angle_from_y(segs[3])
    phi_right = get_angle_from_y(segs[1])
    dir_down = (np.cos(theta_down), np.sin(theta_down))
    dir_up = (np.cos(theta_up), np.sin(theta_up))
    dir_left = (np.sin(phi_left), np.cos(phi_left))
    dir_right = (np.sin(phi_right), np.cos(phi_right))
    return dir_down, dir_up, dir_left, dir_right

def is_between_vectors(A, B, V):
    # Calcul des produits vectoriels
    cross1 = A[0] * V[1] - A[1] * V[0]
    cross2 = V[0] * B[1] - V[1] * B[0]

    # Vérifie si les produits vectoriels ont le même signe
    return cross1 * cross2 >= 0

def intersection_droites_parametriques(p1, v1, p2, v2):
    """
    Trouve l'intersection de deux droites définies par :
    - p1 : point d'origine de la première droite (x1, y1)
    - v1 : vecteur directeur de la première droite (vx1, vy1)
    - p2 : point d'origine de la deuxième droite (x2, y2)
    - v2 : vecteur directeur de la deuxième droite (vx2, vy2)

    Retourne le point d'intersection (x, y) ou None si les droites sont parallèles.
    """
    # Extraire les coordonnées
    x1, y1 = p1
    vx1, vy1 = v1
    x2, y2 = p2
    vx2, vy2 = v2

    # Construire le système linéaire pour résoudre t1 et t2
    A = np.array([[vx1, -vx2], [vy1, -vy2]])  # Matrice des coefficients
    B = np.array([x2 - x1, y2 - y1])  # Côté droit du système

    # Calcul du déterminant
    det = np.linalg.det(A)

    if abs(det) < 1e-9:
        # Si le déterminant est proche de zéro, les droites sont parallèles
        return None

    # Résoudre le système linéaire pour trouver t1 et t2
    t = np.linalg.solve(A, B)
    t1 = t[0]

    # Calculer le point d'intersection
    intersection_x = x1 + t1 * vx1
    intersection_y = y1 + t1 * vy1

    return (intersection_x, intersection_y)

def get_axes_x_y_intersection_ratio(frame, foot_position, keypoints, draw):
    # Définition des points clés
    kp_hl, kp_hr, kp_br, kp_bl = (keypoints[0:2], keypoints[2:4], keypoints[4:6], keypoints[6:8])
    dir_down, dir_up, dir_left, dir_right = get_axes_direct(keypoints)

    # Calcul des intersections des axes de perspective
    inter_y = intersection_droites_parametriques(kp_hl, dir_left, kp_hr, dir_right)
    inter_x = intersection_droites_parametriques(kp_hl, dir_up, kp_bl, dir_down)

    if inter_x is None or inter_y is None:
        return None, None

    # Vecteurs normalisés des intersections vers la position des pieds
    vect_y = normalize((inter_y[0] - foot_position[0], inter_y[1] - foot_position[1]))
    vect_x = normalize((inter_x[0] - foot_position[0], inter_x[1] - foot_position[1]))

    # Option de dessin des lignes de perspective
    if draw:
        for inter, vect in [(inter_x, vect_x), (inter_y, vect_y)]:
            dx, dy = int(foot_position[0] - inter[0]), int(foot_position[1] - inter[1])
            cv2.line(frame, (int(inter[0]), int(inter[1])),
                     (int(foot_position[0] + dx * 5), int(foot_position[1] + dy * 5)),
                     (255, 255, 255), 1)

    # Vérification que la personne est dans le cadre
    vect_pers = (foot_position[0] - kp_hl[0], foot_position[1] - kp_hl[1])
    if not is_between_vectors(dir_up, dir_left, vect_pers):
        return None, None

    # Détection des intersections avec les segments du cadre
    inter_y_left = detect_intersection_seg_vect(inter_x, vect_x, kp_hl, kp_bl)
    inter_x_up = detect_intersection_seg_vect(inter_y, vect_y, kp_hl, kp_hr)

    # Calcul des ratios horizontaux et verticaux
    Ox = get_distance_from_origin(kp_hl, inter_x_up)
    Oy = get_distance_from_origin(kp_hl, inter_y_left)
    up, right, down, left = get_segs_norms(keypoints)

    ratio_h = Ox / up if up else None
    ratio_v = Oy / left if left else None

    return ratio_h, ratio_v
