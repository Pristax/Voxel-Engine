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
        heightmap = np.zeros(CHUNK_AREA, dtype="int16")

        cx, cy, cz = glm.ivec3(self.position) * CHUNK_SIZE

        self.generate_terrain(voxels, heightmap, cx, cy, cz)
        self.generate_trees(voxels, heightmap, cx, cz)

        if np.any(voxels):
            self.is_empty = False

        return voxels

    @staticmethod
    @njit
    def generate_terrain(voxels, heightmap, cx, cy, cz):
        for x in range(CHUNK_SIZE):
            wx = x + cx
            for z in range(CHUNK_SIZE):
                wz = z + cz

                world_height = get_height(wx, wz)
                local_height = max(0, min(world_height - cy, CHUNK_SIZE))

                heightmap[x + CHUNK_SIZE * z] = local_height - 1

                for y in range(local_height):
                    wy = y + cy
                    set_voxel_id(voxels, x, y, z, wx, wy, wz, world_height)

    @staticmethod
    def get_index_py(x, y, z):
        return x + CHUNK_SIZE * z + CHUNK_AREA * y

    @staticmethod
    def generate_trees(voxels, heightmap, cx, cz):
        chance = int(TREE_PROBABILITY * 10000)

        for x in range(TREE_H_WIDTH, CHUNK_SIZE - TREE_H_WIDTH):
            wx = x + cx

            for z in range(TREE_H_WIDTH, CHUNK_SIZE - TREE_H_WIDTH):
                wz = z + cz

                y = int(heightmap[x + CHUNK_SIZE * z])

                if y <= 0:
                    continue

                index = Chunk.get_index_py(x, y, z)

                if voxels[index] != GRASS:
                    continue

                value = (wx * 928371 + wz * 123457 + y * 64513 + SEED * 99991) % 10000

                if value >= chance:
                    continue

                Chunk.place_tree_py(voxels, x, y, z, wx, wz)

    @staticmethod
    def place_tree_py(voxels, x, y, z, wx=0, wz=0):

        rnd = (wx * 928371 + wz * 123457 + SEED * 99991) & 0xFFFFFFFF

        height_variation = rnd % 3 - 1
        tree_height = max(5, TREE_HEIGHT + height_variation)

        trunk_height = max(4, tree_height - TREE_H_HEIGHT)

        if y + tree_height + 1 >= CHUNK_SIZE:
            return

        if x - TREE_H_WIDTH - 1 < 0 or x + TREE_H_WIDTH + 1 >= CHUNK_SIZE:
            return

        if z - TREE_H_WIDTH - 1 < 0 or z + TREE_H_WIDTH + 1 >= CHUNK_SIZE:
            return

        voxels[Chunk.get_index_py(x, y, z)] = DIRT

        for iy in range(1, trunk_height + 1):
            voxels[Chunk.get_index_py(x, y + iy, z)] = WOOD

        branch_y = y + trunk_height - 1

        if branch_y > y + 2:
            if rnd % 2 == 0 and x + 1 < CHUNK_SIZE:
                voxels[Chunk.get_index_py(x + 1, branch_y, z)] = WOOD
            if rnd % 3 == 0 and x - 1 >= 0:
                voxels[Chunk.get_index_py(x - 1, branch_y, z)] = WOOD
            if rnd % 5 == 0 and z + 1 < CHUNK_SIZE:
                voxels[Chunk.get_index_py(x, branch_y, z + 1)] = WOOD
            if rnd % 7 == 0 and z - 1 >= 0:
                voxels[Chunk.get_index_py(x, branch_y, z - 1)] = WOOD

        crown_center_y = y + trunk_height
        crown_radius = TREE_H_WIDTH + 1
        crown_height = TREE_H_HEIGHT + 2

        for ly in range(-1, crown_height):
            py = crown_center_y + ly

            if py <= y or py >= CHUNK_SIZE:
                continue

            layer_radius = crown_radius

            if ly <= 0:
                layer_radius = crown_radius - 1
            elif ly >= crown_height - 2:
                layer_radius = max(1, crown_radius - 2)

            for lx in range(-layer_radius, layer_radius + 1):
                px = x + lx

                if px < 0 or px >= CHUNK_SIZE:
                    continue

                for lz in range(-layer_radius, layer_radius + 1):
                    pz = z + lz

                    if pz < 0 or pz >= CHUNK_SIZE:
                        continue

                    dist = lx * lx + lz * lz

                    if dist > layer_radius * layer_radius + 1:
                        continue

                    # náhodné vykousnutí rohů / okrajů
                    leaf_rand = (
                        px * 734287
                        + py * 912931
                        + pz * 438289
                        + SEED * 19349663
                    ) & 0xFFFFFFFF

                    is_edge = dist >= layer_radius * layer_radius - 1

                    if is_edge and leaf_rand % 100 < 35:
                        continue

                    # neprepisuj kmen uprostřed
                    index = Chunk.get_index_py(px, py, pz)

                    if voxels[index] != WOOD:
                        voxels[index] = LEAVES

        top_y = y + tree_height

        if top_y < CHUNK_SIZE:
            voxels[Chunk.get_index_py(x, top_y, z)] = LEAVES

            if x + 1 < CHUNK_SIZE:
                voxels[Chunk.get_index_py(x + 1, top_y - 1, z)] = LEAVES
            if x - 1 >= 0:
                voxels[Chunk.get_index_py(x - 1, top_y - 1, z)] = LEAVES
            if z + 1 < CHUNK_SIZE:
                voxels[Chunk.get_index_py(x, top_y - 1, z + 1)] = LEAVES
            if z - 1 >= 0:
                voxels[Chunk.get_index_py(x, top_y - 1, z - 1)] = LEAVES