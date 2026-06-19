from settings import *
from meshes.chunk_mesh import ChunkMesh
import random
from terrain_gen import *


class Chunk:
    def __init__(self, world, position):
        self.app = world.app
        self.world = world
        self.position = position
        self.m_model = self.get_model_matrix()
        self.voxels: np.array = None
        self.mesh: ChunkMesh = None
        self.is_empty = True

        self.center = (glm.vec3(self.position) + 0.5) * CHUNK_SIZE
        self.is_on_frustum = self.app.player.frustum.is_on_frustum

    def get_model_matrix(self):
        m_model = glm.translate(glm.mat4(), glm.vec3(self.position) * CHUNK_SIZE)
        return m_model

    def set_uniform(self):
        self.mesh.program["m_model"].write(self.m_model)

    def build_mesh(self):
        self.mesh = ChunkMesh(self)

    def render(self):
        if not self.is_empty and self.is_on_frustum(self):
            self.set_uniform()
            self.mesh.render()

    def build_voxels(self):
        voxels = np.zeros(CHUNK_VOL, dtype="uint8")

        cx, cy, cz = glm.ivec3(self.position) * CHUNK_SIZE

        self.generate_terrain(voxels, cx, cy, cz)
        self.generate_trees(voxels)

        if np.any(voxels):
            self.is_empty = False

        return voxels

    @staticmethod
    @njit
    def generate_terrain(voxels, cx, cy, cz):
        for x in range(CHUNK_SIZE):
            wx = x + cx
            for z in range(CHUNK_SIZE):
                wz = z + cz
                world_height = get_height(wx, wz)
                local_height = min(world_height - cy, CHUNK_SIZE)

                for y in range(local_height):
                    wy = y + cy
                    set_voxel_id(voxels, x, y, z, wx, wy, wz, world_height)

    @staticmethod
    def get_index_py(x, y, z):
        return x + CHUNK_SIZE * z + CHUNK_AREA * y

    @staticmethod
    def generate_trees(voxels):
        for x in range(TREE_H_WIDTH, CHUNK_SIZE - TREE_H_WIDTH):
            for z in range(TREE_H_WIDTH, CHUNK_SIZE - TREE_H_WIDTH):

                for y in range(CHUNK_SIZE - TREE_HEIGHT - 1, 0, -1):
                    index = Chunk.get_index_py(x, y, z)
                    voxel_id = voxels[index]

                    if voxel_id == GRASS:
                        if np.random.random() < TREE_PROBABILITY:
                            Chunk.place_tree_py(voxels, x, y, z)
                        break

                    elif voxel_id != 0:
                        break

    @staticmethod
    def place_tree_py(voxels, x, y, z):
        if y + TREE_HEIGHT >= CHUNK_SIZE:
            return

        if x - TREE_H_WIDTH < 0 or x + TREE_H_WIDTH >= CHUNK_SIZE:
            return

        if z - TREE_H_WIDTH < 0 or z + TREE_H_WIDTH >= CHUNK_SIZE:
            return

        voxels[Chunk.get_index_py(x, y, z)] = DIRT

        # kmen
        trunk_height = TREE_HEIGHT - TREE_H_HEIGHT

        for iy in range(1, trunk_height + 1):
            voxels[Chunk.get_index_py(x, y + iy, z)] = WOOD

        # listy
        leaves_start = y + trunk_height
        leaves_end = y + TREE_HEIGHT

        for ly in range(leaves_start, leaves_end + 1):
            relative_y = ly - leaves_start

            radius = TREE_H_WIDTH

            if relative_y > TREE_H_HEIGHT // 2:
                radius = max(1, TREE_H_WIDTH - 1)

            if ly == leaves_end:
                radius = 1

            for lx in range(-radius, radius + 1):
                for lz in range(-radius, radius + 1):
                    px = x + lx
                    py = ly
                    pz = z + lz

                    if px < 0 or px >= CHUNK_SIZE:
                        continue

                    if py < 0 or py >= CHUNK_SIZE:
                        continue

                    if pz < 0 or pz >= CHUNK_SIZE:
                        continue

                    # neprepisuj kmen listím
                    if lx == 0 and lz == 0 and ly <= y + trunk_height:
                        continue

                    voxels[Chunk.get_index_py(px, py, pz)] = LEAVES