from math import pi, tan

import pygame

from mesh import Mesh
from util import (FORWARD, Vec3, clip_polygon, color_mult, draw_text,
                  map_range, rotate_by_vec, z_average)

LIGHT = Vec3(-1, -1, -0.5).normalize()
LIGHT_COLOR = (255, 200, 200)


class Camera:
    VERTICES = 1
    EDGES = 2
    FACES = 4

    L_FLAT = 1
    L_SHADED = 2
    L_FACE_UNIQUE = 3


    def __init__(self, fov, near, far, pos, rot):
        self._p_mat = self.build_p_mat(fov, near, far)
        self.fov = fov
        self.near = near
        self.far = far
        self.pos = Vec3(pos)
        self.rot = Vec3(rot)
        self.points = []
        self.lines = []
        self.faces = []
        self.drawmode = 7
        self.lightmode = 2
        self.viewport = None

    # Maintenance Methods
    def build_p_mat(self, fov, near, far, a=1):
        p_mat = [[0, 0, 0, 0] for _ in range(4)]
        S = 1 / tan(fov * 0.5 * pi / 180)
        q = -far / (far - near)
        p_mat = [
            [a * S, 0, 0, 0],
            [0, S, 0, 0],
            [0, 0, q, -1],
            [0, 0, near * q, 0],
        ]
        return p_mat

    def set_viewport(self, dimx, dimy):
        self.viewport = pygame.Surface((dimx, dimy))
        if dimx != dimy:
            self._p_mat = self.build_p_mat(self.fov, self.near, self.far, dimy / dimx)

    def set_drawmode(self, drawmode):
        self.drawmode = drawmode


    # Utility Methods
    def project(self, v_in: Vec3):
        out = Vec3()
        out.x = (
            v_in.x * self._p_mat[0][0]
            + v_in.y * self._p_mat[1][0]
            + v_in.z * self._p_mat[2][0]
            + self._p_mat[3][0]
        )
        out.y = (
            v_in.x * self._p_mat[0][1]
            + v_in.y * self._p_mat[1][1]
            + v_in.z * self._p_mat[2][1]
            + self._p_mat[3][1]
        )
        out.z = (
            v_in.x * self._p_mat[0][2]
            + v_in.y * self._p_mat[1][2]
            + v_in.z * self._p_mat[2][2]
            + self._p_mat[3][2]
        )
        w = (
            v_in.x * self._p_mat[0][2]
            + v_in.y * self._p_mat[1][3]
            + v_in.z * self._p_mat[2][3]
            + self._p_mat[3][3]
        )

        if w != 1 and w != 0:
            out.x /= w
            out.y /= w
            out.z /= w
        return out

    def back_face_cull(self, face):
        normal = Vec3(face[1] - face[0]).cross(Vec3(face[2] - face[1]))
        return normal, normal.dot(FORWARD) > 0

    def to_camera_space(self, v_in: Vec3):
        v_out = v_in - self.pos
        return rotate_by_vec(v_out, self.rot)

    def clear(self):
        self.points = []
        self.lines = []
        self.faces = []

    def camera_forward(self):
        cam_forward = FORWARD.copy()
        cam_forward.rotate_x_ip(-self.rot.x)
        cam_forward.rotate_y_ip(-self.rot.y)
        return cam_forward
    
    def get_face_color(self, mesh, face_index):
        color = (0, 0, 0)
        if self.lightmode == self.L_FLAT:
            color = mesh.color
        if self.lightmode == self.L_SHADED:
            normal = mesh.face_normal(face_index)
            l_intensity = map_range(LIGHT.dot(normal), -1, 0, 1, 0)
            l_color = color_mult(LIGHT_COLOR, l_intensity)
            color = (
                (l_color[0] + mesh.color[0]) / 2,
                (l_color[1] + mesh.color[1]) / 2,
                (l_color[2] + mesh.color[2]) / 2,
            )
        elif self.lightmode == self.L_FACE_UNIQUE:
            color = Mesh._colors[face_index]
        return color
    
    # Graphics Methods
    def render(self, mesh: Mesh):
        vertices = mesh.vertices()
        cs_vertices = []
        for vert in vertices:
            cs_vertices.append(self.to_camera_space(vert))
            # p_vert = self.project(cs_vert)

            # if 0 <= p_vert.z <= 1 and -1 <= p_vert.x <= 1 and -1 <= p_vert.y <= 1:
            #     self.points.append(p_vert)

        for num, face in enumerate(mesh._faces):
            face = (cs_vertices[face[0]], cs_vertices[face[1]], cs_vertices[face[2]])
            face = clip_polygon(face, zmin=-self.far, zmax=-self.near)
            if not face:
                continue
            z = z_average(face)
            face = [self.project(point) for point in face]
            _, cull = self.back_face_cull(face)
            if cull:
                continue
            if face:
                self.faces.append((face, self.get_face_color(mesh, num), z))

    def render_multi(self, meshs: list):
        for mesh in meshs:
            self.render(mesh)

    def draw(self, surface, pos):
        if self.viewport is None:
            return
        dimx = self.viewport.get_width()
        dimy = self.viewport.get_height()
        self.viewport.fill("black")
        # print(self.faces)
        if self.faces:
            self.faces.sort(
                reverse=False,
                key=lambda face_data: face_data[2],
            )

            for face, color, _ in self.faces:
                points = [
                    (map_range(p.x, -1, 1, 0, dimx), map_range(p.y, 1, -1, 0, dimy))
                    for p in face
                ]
                if self.drawmode & self.FACES:
                    pygame.draw.polygon(self.viewport, color, points)

                if self.drawmode & self.EDGES:
                    for i in range(len(points)):
                        pygame.draw.line(
                            self.viewport, "white", points[i - 1], points[i]
                        )

        if self.drawmode & self.VERTICES:
            for num, point in enumerate(self.points):
                x = map_range(point.x, -1, 1, 0, dimx)
                y = map_range(point.y, 1, -1, 0, dimy)
                pygame.draw.circle(self.viewport, "blue", (x, y), 2)
                #draw_text(self.viewport, str(num), (x, y))

        surface.blit(self.viewport, pos)
