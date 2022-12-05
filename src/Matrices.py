from math import *
from Base3DObjects import *

class ModelMatrix:
	def __init__(self):
		self.matrix = [ 1, 0, 0, 0,
						0, 1, 0, 0,
						0, 0, 1, 0,
						0, 0, 0, 1 ]
		self.stack = []
		self.stack_count = 0
		self.stack_capacity = 0

	def load_identity(self):
		self.matrix = [ 1, 0, 0, 0,
						0, 1, 0, 0,
						0, 0, 1, 0,
						0, 0, 0, 1 ]

	def copy_matrix(self):
		new_matrix = [0] * 16
		for i in range(16):
			new_matrix[i] = self.matrix[i]
		return new_matrix

	def add_transformation(self, matrix2):
		counter = 0
		new_matrix = [0] * 16
		for row in range(4):
			for col in range(4):
				for i in range(4):
					new_matrix[counter] += self.matrix[row*4 + i]*matrix2[col + 4*i]
				counter += 1
		self.matrix = new_matrix

	def add_translation(self, x, y, z):
		other_matrix = [1, 0, 0, x,
						0, 1, 0, y,
						0, 0, 1, z,
						0, 0, 0, 1]
		self.add_transformation(other_matrix)
	
	def add_scale(self, Sx, Sy, Sz):
		other_matrix = [Sx, 0,  0,  0,
						0,  Sy, 0,  0,
						0,  0,  Sz, 0,
						0,  0,  0,  1]
		self.add_transformation(other_matrix)
	
	def add_rotation(self, x, y, z):
		x = self.add_rotation_x(x * pi / 180.0)
		y = self.add_rotation_y(y * pi / 180.0)
		z = self.add_rotation_z(z * pi / 180.0)
	
	def add_rotation_x(self, angle):
		c = cos(angle)
		s = sin(angle)
		other_matrix = [1, 0, 0,  0,
						0, c, -s, 0,
						0, s, c,  0,
						0, 0, 0,  1]
		self.add_transformation(other_matrix)
	
	def add_rotation_y(self, angle):
		c = cos(angle)
		s = sin(angle)
		other_matrix = [c,  0, s, 0,
						0,  1, 0, 0,
						-s, 0, c, 0,
						0,  0, 0, 1]
		self.add_transformation(other_matrix)
	
	def add_rotation_z(self, angle):
		c = cos(angle)
		s = sin(angle)
		other_matrix = [c, -s, 0, 0,
						s, c,  0, 0,
						0, 0,  1, 0,
						0, 0,  0, 1]
		self.add_transformation(other_matrix)

	# YOU CAN TRY TO MAKE PUSH AND POP (AND COPY) LESS DEPENDANT ON GARBAGE COLLECTION
	# THAT CAN FIX SMOOTHNESS ISSUES ON SOME COMPUTERS
	def push_matrix(self):
		self.stack.append(self.copy_matrix())

	def pop_matrix(self):
		self.matrix = self.stack.pop()

	# This operation mainly for debugging
	def __str__(self):
		ret_str = ""
		counter = 0
		for _ in range(4):
			ret_str += "["
			for _ in range(4):
				ret_str += " " + str(self.matrix[counter]) + " "
				counter += 1
			ret_str += "]\n"
		return ret_str

# The Camera class holds the camera's coordinate frame and
# set's up a transformation concerning the camera's position
# and orientation
class Camera:
	def __init__(self):
		self.eye = Point(0, 0, 0)
		self.u = Vector(1, 0, 0)
		self.v = Vector(0, 1, 0)
		self.n = Vector(0, 0, 1)

	def look(self, eye, center, up):
		self.eye = eye
		self.n = eye - center
		self.u = up.cross(self.n)
		self.n.normalize()
		self.u.normalize()
		self.v = self.n.cross(self.u)

	def get_velocity(self, world_space_vel):
		return self.u * world_space_vel.x + self.v * world_space_vel.y + self.n * world_space_vel.z

	def move(self, vel):
		self.eye += vel

	def yaw(self, angle):
		c = cos(angle)
		s = sin(angle)

		temp_n = self.n * c + self.u * s
		self.u = self.n * -s + self.u * c
		self.n = temp_n

	def get_matrix(self):
		minusEye = Vector(-self.eye.x, -self.eye.y, -self.eye.z)
		return [self.u.x, self.u.y, self.u.z, minusEye.dot(self.u),
				self.v.x, self.v.y, self.v.z, minusEye.dot(self.v),
				self.n.x, self.n.y, self.n.z, minusEye.dot(self.n),
				0,        0,        0,        1]

# The ProjectionMatrix class builds transformations concerning
# the camera's "lens"
class ProjectionMatrix:
	def __init__(self):
		self.left = -1
		self.right = 1
		self.bottom = -1
		self.top = 1
		self.near = -1
		self.far = 1

		self.is_orthographic = True

	def set_perspective(self, fovy, aspect, near, far):
		self.near = near
		self.far = far
		self.top = near * tan(fovy / 2)
		self.bottom = -self.top
		self.right = self.top * aspect
		self.left = -self.right
		self.is_orthographic = False

	def set_orthographic(self, left, right, bottom, top, near, far):
		self.left = left
		self.right = right
		self.bottom = bottom
		self.top = top
		self.near = near
		self.far = far
		self.is_orthographic = True

	def get_matrix(self):
		if self.is_orthographic:
			A = 2 / (self.right - self.left)
			B = -(self.right + self.left) / (self.right - self.left)
			C = 2 / (self.top - self.bottom)
			D = -(self.top + self.bottom) / (self.top - self.bottom)
			E = 2 / (self.near - self.far)
			F = (self.near + self.far) / (self.near - self.far)

			return [A,0,0,B,
					0,C,0,D,
					0,0,E,F,
					0,0,0,1]
		else:
			A = (2 * self.near) / (self.right - self.left)
			B = (self.right + self.left) / (self.right - self.left)
			C = (2 * self.near) / (self.top - self.bottom)
			D = (self.top + self.bottom) / (self.top - self.bottom)
			E = -(self.far + self.near) / (self.far - self.near)
			F = -(2 * self.far * self.near) / (self.far - self.near)

			return [A,0,B, 0,
					0,C,D, 0,
					0,0,E, F,
					0,0,-1,0]
