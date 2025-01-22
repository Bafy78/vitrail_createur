import drawsvg as draw
import random
import math
import numpy as np
from PIL import Image
from shapely.geometry import Polygon, Point
from scipy.spatial import Voronoi
import colorsys

# ------------------------------------------------------------------
# 1. Paramètres globaux
# ------------------------------------------------------------------
CANVAS_WIDTH, CANVAS_HEIGHT = 2800, 1500
FRAME_WIDTH, FRAME_HEIGHT = 900, 1300
NUM_SHAPES = 2000
FRAME_X = (CANVAS_WIDTH - FRAME_WIDTH) / 2
FRAME_Y = (CANVAS_HEIGHT - FRAME_HEIGHT) / 2
RESPIRATION_PROBABILITY = 0.08  # Probabilité qu'un polygone soit animé
RESPIRATION_SCALE = 1.004
TILT_ANGLE = 8                 # Amplitude maximum de rotation en degrés

# ------------------------------------------------------------------
# 2. Traitement de l'image
# ------------------------------------------------------------------
def load_and_process_image(image_path):
    original_img = Image.open(image_path).convert("RGB")
    orig_w, orig_h = original_img.size
    ratio = (FRAME_HEIGHT / orig_h) * 0.8
    new_w, new_h = int(orig_w * ratio), FRAME_HEIGHT
    resized_img = original_img.resize((new_w, new_h), Image.LANCZOS)

    # Créer une image de fond et y coller l'image redimensionnée
    final_img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), (26, 26, 26))
    start_x = (CANVAS_WIDTH - new_w) // 2
    start_y = int(FRAME_Y)
    final_img.paste(resized_img, (start_x, start_y))
    return np.array(final_img)

# ------------------------------------------------------------------
# 3. Géométrie : cadre arrondi et polygones Voronoi
# ------------------------------------------------------------------
def build_frame_path():
    frame_radius = FRAME_WIDTH / 2
    arc_center_x = FRAME_X + frame_radius
    arc_center_y = FRAME_Y + frame_radius

    path = []
    for angle_deg in range(180, 361, 10):
        angle = math.radians(angle_deg)
        x = arc_center_x + frame_radius * math.cos(angle)
        y = arc_center_y + frame_radius * math.sin(angle)
        path.append((x, y))
    path += [
        (FRAME_X + FRAME_WIDTH, FRAME_Y + FRAME_HEIGHT),
        (FRAME_X, FRAME_Y + FRAME_HEIGHT),
        path[0]
    ]
    return Polygon(path), path

def generate_voronoi_polygons(frame_poly, num_points):
    minx, miny, maxx, maxy = frame_poly.bounds

    # Génération de points internes avec des points fixes proches des bords
    points = [(random.uniform(minx, maxx), random.uniform(miny, maxy)) for _ in range(num_points)]
    border_points = [
        (x, miny + 1) for x in np.linspace(minx, maxx, 20)
    ] + [
        (x, maxy - 1) for x in np.linspace(minx, maxx, 20)
    ] + [
        (minx + 1, y) for y in np.linspace(miny, maxy, 20)
    ] + [
        (maxx - 1, y) for y in np.linspace(miny, maxy, 20)
    ]
    points.extend(border_points)

    # Calcul des Voronoi
    vor = Voronoi(points)
    polygons = []

    for region_idx in vor.regions:
        if not region_idx or (-1 in region_idx):
            continue
        poly_coords = [vor.vertices[i] for i in region_idx]
        shapely_poly = Polygon(poly_coords)
        if shapely_poly.is_valid and not shapely_poly.is_empty:
            inter = shapely_poly.intersection(frame_poly)
            if inter.geom_type == 'Polygon' and inter.area > 0.1:  # Ignorer les polygones trop petits
                polygons.append(list(inter.exterior.coords))
            elif inter.geom_type == 'MultiPolygon':
                for subpoly in inter.geoms:
                    if subpoly.area > 0.1:
                        polygons.append(list(subpoly.exterior.coords))
    return polygons

# ------------------------------------------------------------------
# 4. Calcul de la couleur moyenne et transformation HSL
# ------------------------------------------------------------------
def average_color_in_polygon(image_array, polygon):
    poly = Polygon(polygon)
    min_x, min_y, max_x, max_y = map(int, poly.bounds)
    h, w, _ = image_array.shape
    pixels = []

    for y in range(min_y, max_y + 1):
        if 0 <= y < h:
            for x in range(min_x, max_x + 1):
                if 0 <= x < w:
                    if poly.contains(Point(x, y)):
                        pixels.append(image_array[y, x])

    if pixels:
        avg_color = np.mean(pixels, axis=0)
        return avg_color.astype(int)
    return np.array([0, 0, 0])

def rgb_to_hsl(r, g, b):
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
    h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)
    return h * 360, s * 100, l * 100

def hsl_to_rgb(h, s, l):
    h_norm, s_norm, l_norm = h / 360.0, s / 100.0, l / 100.0
    r, g, b = colorsys.hls_to_rgb(h_norm, l_norm, s_norm)
    return int(r * 255), int(g * 255), int(b * 255)

# ------------------------------------------------------------------
# 5. Génération du dessin SVG
# ------------------------------------------------------------------
def create_vitrail(image_path, output_svg):
    image_array = load_and_process_image(image_path)
    frame_poly, frame_path = build_frame_path()
    voronoi_polygons = generate_voronoi_polygons(frame_poly, NUM_SHAPES)

    vitral = draw.Drawing(CANVAS_WIDTH, CANVAS_HEIGHT, origin=(0, 0), displayInline=False)
    vitral.append(draw.Rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill="#1A1A1A"))

    # Création des calques
    static_layer = draw.Group(id="static-layer")
    animated_layer = draw.Group(id="animated-layer")

    # Ajout des polygones Voronoi
    for polygon in voronoi_polygons:
        if len(polygon) < 3:
            continue
        avg_rgb = average_color_in_polygon(image_array, polygon)
        h, s, l = rgb_to_hsl(*avg_rgb)

        points = [coord for vertex in polygon for coord in vertex]

        # Ombre portée
        shadow_poly = draw.Lines(*[coord + 2 for coord in points], close=True,
                                  fill="rgba(0, 0, 0, 0.5)", stroke="none")
        static_layer.append(shadow_poly)

        poly = draw.Lines(*points, close=True, fill=f'rgb({avg_rgb[0]},{avg_rgb[1]},{avg_rgb[2]})', stroke="black", stroke_width=2)

        # Animation de la couleur (variation cyclique de la teinte)
        anim_values = ";".join([
            f'rgb({hsl_to_rgb((h + i) % 360, s, l)[0]},' +
            f'{hsl_to_rgb((h + i) % 360, s, l)[1]},' +
            f'{hsl_to_rgb((h + i) % 360, s, l)[2]})'
            for i in range(0, 361, 60)
        ])
        anim_color = draw.Animate(
            "fill", 
            dur="6s", 
            values=anim_values, 
            calcMode="linear", 
            repeatCount="indefinite"
        )
        poly.append_anim(anim_color)

        # Animation de "respiration" aléatoire + de rotation lors du détachement
        if random.random() < RESPIRATION_PROBABILITY:
            delay = f"{random.uniform(0, 4):.2f}s"

            # 1) Animation de SCALE (inchangée)
            anim_scale = draw.AnimateTransform(
                attributeName="transform",
                attributeType="XML",
                type="scale",
                dur="4s",
                from_or_values=f"1;{RESPIRATION_SCALE};1",
                begin=delay,
                calcMode="spline",
                keySplines="0.25 0.1 0.25 1;0.25 0.1 0.25 1",
                repeatCount="indefinite"
            )
            poly.append_anim(anim_scale)

            # 2) Récupérer le polygone Shapely
            shapely_poly = Polygon([(points[i], points[i+1]) 
                                    for i in range(0, len(points), 2)])
            coords = list(shapely_poly.exterior.coords)
            
            lowest_corner = min(coords, key=lambda c: c[1])
            corner_x, corner_y = lowest_corner

            # 3) Animation de ROTATION autour de ce coin
            anim_rotate = draw.AnimateTransform(
                attributeName="transform",
                attributeType="XML",
                type="rotate",
                dur="4s",
                from_or_values=(
                    f"0 {corner_x} {corner_y};"
                    f"{TILT_ANGLE} {corner_x} {corner_y};"
                    f"{-TILT_ANGLE/4} {corner_x} {corner_y};"
                    f"0 {corner_x} {corner_y};"
                    f"0 {corner_x} {corner_y}"
                ),
                begin=delay,
                calcMode="spline",
                keyTimes="0;0.05;0.15;0.25;1",
                keySplines="0.8 0 1 1;0.8 0 1 1;0.8 0 1 1;0.8 0 1 1",
                additive="sum",   # IMPORTANT pour cumuler scale + rotate
                repeatCount="indefinite"
            )
            poly.append_anim(anim_rotate)

            animated_layer.append(poly)
        else:
            static_layer.append(poly)

    # Ajouter les calques au dessin
    vitral.append(static_layer)
    vitral.append(animated_layer)

    # Ajout du cadre avec une bordure agrandie et un dégradé
    frame_path_str = (
        f"M {frame_path[0][0]} {frame_path[0][1]} " +
        " ".join(f"L {x} {y}" for x, y in frame_path[1:]) +
        " Z"
    )
    frame_gradient = draw.LinearGradient(
        0, 0, 1, 0, gradientUnits="objectBoundingBox")
    frame_gradient.add_stop(0, "gold")
    frame_gradient.add_stop(1, "darkorange")

    vitral.append(draw.Path(d=frame_path_str, fill="none", stroke=frame_gradient, stroke_width=8))

    vitral.save_svg(output_svg)

# ------------------------------------------------------------------
# 6. Appel principal
# ------------------------------------------------------------------
if __name__ == "__main__":
    create_vitrail("pouler.png", "pouler.svg")