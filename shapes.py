from util import Vec3


class Box:
    def __init__(self, w, h, d):
        w = w / 2
        h = h / 2
        d = d / 2
        self.vertices = (
            Vec3(w, h, d),
            Vec3(-w, h, d),
            Vec3(-w, -h, d),
            Vec3(w, -h, d),
            Vec3(w, h, -d),
            Vec3(-w, h, -d),
            Vec3(-w, -h, -d),
            Vec3(w, -h, -d),
        )
        # ABCD, EFGH, ABFE, DCGH, AEHD, BFGC.
        self.faces = (
            (0, 1, 2),
            (0, 2, 3),
            (5, 7, 6),
            (5, 4, 7),
            (3, 7, 4),
            (4, 0, 3),
            (6, 2, 1),
            (1, 5, 6),
            (1, 0, 4),
            (4, 5, 1),
            (6, 7, 3),
            (3, 2, 6),
        )


class Triangle:
    def __init__(self, w, h):
        self.vertices = (Vec3(0, 0, 0), Vec3(w, 0, 0), Vec3(w / 2, h, 0))
        self.faces = ((0, 1, 2),)


class Quad:
    def __init__(self, w, h):
        self.vertices = (
            Vec3(-w / 2, h / 2, 0),
            Vec3(w / 2, h / 2, 0),
            Vec3(w / 2, -h / 2, 0),
            Vec3(-w / 2, -h / 2, 0),
        )
        self.faces = ((0, 1, 2), (2, 3, 0))


class NoShape:
    def __init__(self):
        self.vertices = []
        self.faces = []
