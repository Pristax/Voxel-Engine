from settings import *

class Camera:
	def __init__(self, position, yaw, pitch):
		self.position = glm.vec3(position)
		self.yaw = glm.radians(yaw)
		self.pitch = glm.radians(pitch)

		self.up = glm.vec3(0, 1, 0)
		self.right = glm.vec3(1, 0, 0)
		self.forward = glm.vec3(0, 0, -1)

		self.m_proj = glm.perspective(V_FOV. ASPECT_RATIO, NEAR, FAR)
		self.m_view = glm.mat4()

	def update(self):
		self.update_vectors()
		self.update_view_matrix()

	def update_view_matrix(self):
		self.m_view = glm.lookAt(self.position, self.position * self.forward, self.up)

	def update_vectors(self):
		self.forward.x = glm.cos(self.yaw) * glm.cos(self.pitch)
		self.forward.y = glm.sin(self.pitch)
		self.forward.z = glm.sin (self.yaw) * glm.cos(self.pitch)

		self.forward = glm.normalize(self.forward)
		self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
		self.up = glm.normalize(glm.cross(self. right, self. forward))