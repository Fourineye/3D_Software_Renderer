from random import randint

import pygame

pygame.font.init()

FONT = pygame.font.SysFont(pygame.font.get_fonts()[5], 12)
Vec3 = pygame.Vector3
Vec2 = pygame.Vector2

UP = Vec3(0, 1, 0)
DOWN = Vec3(0, -1, 0)
LEFT = Vec3(-1, 0, 0)
RIGHT = Vec3(1, 0, 0)
FORWARD = Vec3(0, 0, -1)
BACK = Vec3(0, 0, 1)

def map_range(x, a, b, c, d):
    y = (x - a) / (b - a) * (d - c) + c
    return y


def clamp(x, min_, max_):
    return min(max_, max(min_, x))


def rand_color():
    return Vec3(randint(0, 255), randint(0, 255), randint(0, 255))


def color_mult(color, mult):
    m_color = []
    for c in color:
        m_c = clamp(c * mult, 0, 255)
        m_color.append(m_c)
    return m_color


def draw_text(surface: pygame.Surface, text: str, pos: Vec2):
    text_surf = FONT.render(text, True, "white")
    surface.blit(text_surf, pos)


def rotate_by_vec(vec1: Vec3, vec2: Vec3):
    new_vec = Vec3(vec1)
    new_vec.rotate_y_ip(vec2.y)
    new_vec.rotate_x_ip(vec2.x)
    new_vec.rotate_z_ip(vec2.z)
    return new_vec


def z_average(face):
    total = 0
    for point in face:
        total += point.z
    return total / len(face)


def line_intersection(p_0, p_1, p_2, p_3):
    p_0 = pygame.Vector2(p_0)
    p_1 = pygame.Vector2(p_1)
    p_2 = pygame.Vector2(p_2)
    p_3 = pygame.Vector2(p_3)

    s_1 = pygame.Vector2(p_1 - p_0)
    s_2 = pygame.Vector2(p_3 - p_2)

    if abs(s_1.normalize().dot(s_2.normalize())) == 1:
        return None

    s = (-s_1.y * (p_0.x - p_2.x) + s_1.x * (p_0.y - p_2.y)) / (
        -s_2.x * s_1.y + s_1.x * s_2.y
    )
    t = (s_2.x * (p_0.y - p_2.y) - s_2.y * (p_0.x - p_2.x)) / (
        -s_2.x * s_1.y + s_1.x * s_2.y
    )

    if 0 <= s <= 1 and 0 <= t <= 1:
        i = p_0 + (t * s_1)
        return pygame.Vector2(i)
    else:
        return None


def line_plane(plane_p: Vec3, plane_n: Vec3, l_start: Vec3, l_end: Vec3):
    plane_n.normalize_ip()
    plane_d = -plane_n.dot(plane_p)
    ad = l_start.dot(plane_n)
    bd = l_end.dot(plane_n)
    t = (-plane_d - ad) / (bd - ad)
    line = l_end - l_start
    return l_start + line * t

def clip_polygon(
    polygon, xmin=None, ymin=None, zmin=None, xmax=None, ymax=None, zmax=None
):
    def inside(point: tuple, edge: float, axis: str, max_: bool):
        if axis == "x":
            return point.x < edge if max_ else point.x > edge
        if axis == "y":
            return point.y < edge if max_ else point.y > edge
        if axis == "z":
            return point.z < edge if max_ else point.z > edge

    def intersect(p1: Vec3, p2: Vec3, edge: float, axis: str):
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        dz = p2.z - p1.z

        if axis == "x" and abs(dx) > 1e-10:
            t = (edge - p1.x) / dx
            if 0 <= t <= 1:
                y = p1.y + t * dy
                z = p1.z + t * dz
                return Vec3(edge, y, z)

        if axis == "y" and abs(dy) > 1e-10:
            t = (edge - p1.y) / dy
            if 0 <= t <= 1:
                x = p1.x + t * dx
                z = p1.z + t * dz
                return Vec3(x, edge, z)

        if axis == "z" and abs(dz) > 1e-10:
            t = (edge - p1.z) / dz
            if 0 <= t <= 1:
                x = p1.x + t * dx
                y = p1.y + t * dy
                return Vec3(x, y, edge)

        return None

    def clip_edge(polygon, edge, axis, max_):
        clipped_polygon = []
        prev_point = polygon[-1]
        prev_inside = inside(prev_point, edge, axis, max_)
        # print(prev_point, ":", prev_inside)
        for point in polygon:
            curr_inside = inside(point, edge, axis, max_)
            # print(point, ":", curr_inside)

            if prev_inside and curr_inside:
                clipped_polygon.append(point)

            elif prev_inside and not curr_inside:
                intersect_point = intersect(prev_point, point, edge, axis)
                if intersect_point:
                    clipped_polygon.append(intersect_point)

            elif not prev_inside and curr_inside:
                intersect_point = intersect(prev_point, point, edge, axis)
                if intersect_point:
                    clipped_polygon.append(intersect_point)
                clipped_polygon.append(point)

            prev_point = point
            prev_inside = curr_inside

        return clipped_polygon

    # Clip against each edge of the rectangle
    clipped_polygon = polygon
    if clipped_polygon and zmin is not None:
        clipped_polygon = clip_edge(clipped_polygon, zmin, "z", False)

    if clipped_polygon and zmax is not None:
        clipped_polygon = clip_edge(clipped_polygon, zmax, "z", True)

    if clipped_polygon and ymin is not None:
        clipped_polygon = clip_edge(clipped_polygon, ymin, "y", False)

    if clipped_polygon and ymax is not None:
        clipped_polygon = clip_edge(clipped_polygon, ymax, "y", True)

    if clipped_polygon and xmin is not None:
        clipped_polygon = clip_edge(clipped_polygon, xmin, "x", False)

    if clipped_polygon and xmax is not None:
        clipped_polygon = clip_edge(clipped_polygon, xmax, "x", True)

    return clipped_polygon

