from shapes import NoShape
from util import Vec3, rand_color, rotate_by_vec


class Mesh:
    def __init__(
        self, shape, pos: Vec3, rot=(0, 0, 0), color=(255, 255, 255), scale=(1, 1, 1)
    ):
        self._vertices = shape.vertices
        self._faces = shape.faces
        self._colors = [rand_color() for _ in self._faces]
        self.scale = Vec3(scale)
        self.pos = Vec3(pos)
        self.rot = Vec3(rot)
        self.color = color

    @staticmethod
    def from_obj(file_path, pos, rot=(0, 0, 0), color=(255, 255, 255), scale=(1, 1, 1)):
        new_mesh = Mesh(NoShape(), pos, rot, color)
        with open(file_path, "r") as obj:
            for line in obj.readlines():
                line = line.strip()
                line = line.split(" ")
                # print(line)
                if line[0] == "v":
                    new_mesh._vertices.append(
                        Vec3(float(line[1]), float(line[2]), float(line[3]))
                    )
                    # print(new_mesh._vertices[-1])
                if line[0] == "f":
                    face = []
                    for vertex in line[1:]:
                        vertex = vertex.split("/")
                        face.append(int(vertex[0]) - 1)
                    new_mesh._faces.append(tuple(face))
                    # print(new_mesh._faces[-1])
        new_mesh._colors = [rand_color() for _ in new_mesh._faces]
        return new_mesh

    def vertices(self):
        verts = []
        for vert in self._vertices:
            s_vert = Vec3([vert[i] * self.scale[i] for i in range(3)])
            r_vert = rotate_by_vec(vert, self.rot)
            verts.append(r_vert + self.pos)
        return verts

    def face_normal(self, index):
        if not 0 <= index < len(self._faces):
            return None
        face = self._faces[index]
        face = [rotate_by_vec(self._vertices[point], self.rot) for point in face]
        ab = face[1] - face[0]
        bc = face[2] - face[1]
        normal = ab.cross(bc)
        if normal.length_squared() != 0:
            return normal.normalize()
        return normal

    def set_color(self, new_color):
        self.color = new_color
