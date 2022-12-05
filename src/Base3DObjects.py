from random import *
from math import *

from OpenGL.GL import *
from OpenGL.GLU import *

import numpy

class Color:
	def __init__(self, r, g, b):
		self.r = r
		self.g = g
		self.b = b

class Point:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

	def __add__(self, other):
		return Point(self.x + other.x, self.y + other.y, self.z + other.z)

	def __sub__(self, other):
		return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

class Vector:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z
	
	def __add__(self, other):
		return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

	def __sub__(self, other):
		return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

	def __mul__(self, scalar):
		return Vector(self.x * scalar, self.y * scalar, self.z * scalar)
	
	def __len__(self):
		return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
	
	def __str__(self):
		return "(%f, %f, %f)" % (self.x, self.y, self.z)

	def normalize(self):
		length = self.__len__()
		self.x /= length
		self.y /= length
		self.z /= length

	def dot(self, other):
		return self.x * other.x + self.y * other.y + self.z * other.z

	def cross(self, other):
		return Vector(self.y*other.z - self.z*other.y, self.z*other.x - self.x*other.z, self.x*other.y - self.y*other.x)

class Cube:
	def __init__(self, length = 1):
		self.position_array = [
			-0.5, -0.5, -0.5,
			-0.5,  0.5, -0.5,
			 0.5,  0.5, -0.5,
			 0.5, -0.5, -0.5,

			-0.5, -0.5, 0.5,
			-0.5,  0.5, 0.5,
			 0.5,  0.5, 0.5,
			 0.5, -0.5, 0.5,
			
			-0.5, -0.5, -0.5,
			 0.5, -0.5, -0.5,
			 0.5, -0.5,  0.5,
			-0.5, -0.5,  0.5,
			
			-0.5, 0.5, -0.5,
			 0.5, 0.5, -0.5,
			 0.5, 0.5,  0.5,
			-0.5, 0.5,  0.5,
			
			-0.5, -0.5, -0.5,
			-0.5, -0.5,  0.5,
			-0.5,  0.5,  0.5,
			-0.5,  0.5, -0.5,
			
			0.5, -0.5, -0.5,
			0.5, -0.5,  0.5,
			0.5,  0.5,  0.5,
			0.5,  0.5, -0.5,
		]

		self.normal_array = [
			0.0, 0.0, -1.0,
			0.0, 0.0, -1.0,
			0.0, 0.0, -1.0,
			0.0, 0.0, -1.0,

			0.0, 0.0, 1.0,
			0.0, 0.0, 1.0,
			0.0, 0.0, 1.0,
			0.0, 0.0, 1.0,
			
			0.0, -1.0, 0.0,
			0.0, -1.0, 0.0,
			0.0, -1.0, 0.0,
			0.0, -1.0, 0.0,
			
			0.0, 1.0, 0.0,
			0.0, 1.0, 0.0,
			0.0, 1.0, 0.0,
			0.0, 1.0, 0.0,
			
			-1.0, 0.0, 0.0,
			-1.0, 0.0, 0.0,
			-1.0, 0.0, 0.0,
			-1.0, 0.0, 0.0,
			
			1.0, 0.0, 0.0,
			1.0, 0.0, 0.0,
			1.0, 0.0, 0.0,
			1.0, 0.0, 0.0,
		]
		
		self.uv_sx = 0.01 * length # Short size x
		self.uv_sy = 1.0 # Short side y
		self.uv_lx = 0.2 * length # Long side x
		self.uv_ly = 1.0 # Long side y

		self.uv_array = [
			# Short side - correct
			0.0, 0.0,
			0.0, self.uv_sy,
			self.uv_sx, self.uv_sy,
			self.uv_sx, 0.0,

			# Short side - correct
			0.0, 0.0,
			0.0, self.uv_sy,
			self.uv_sx, self.uv_sy,
			self.uv_sx, 0.0,
			
			# Bottom
			20.0, 0.0,
			0.0, 0.0,
			0.0, 20.0,
			20.0, 20.0,
			
			# Top
			20.0, 0.0,
			0.0, 0.0,
			0.0, 20.0,
			20.0, 20.0,

			# Long side, correct
			self.uv_lx, 0.0,
			0.0, 0.0,
			0.0, self.uv_ly,
			self.uv_lx, self.uv_ly,
			
			# Long side, correct
			self.uv_lx, 0.0,
			0.0, 0.0,
			0.0, self.uv_ly,
			self.uv_lx, self.uv_ly,
		]
	
	def set_vertices(self, shader):
		shader.set_position_attribute(self.position_array)
		shader.set_normal_attribute(self.normal_array)
		shader.set_uv_attribute(self.uv_array)

	def draw(self):
		glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
		glDrawArrays(GL_TRIANGLE_FAN, 4, 4)
		glDrawArrays(GL_TRIANGLE_FAN, 8, 4)
		glDrawArrays(GL_TRIANGLE_FAN, 12, 4)
		glDrawArrays(GL_TRIANGLE_FAN, 16, 4)
		glDrawArrays(GL_TRIANGLE_FAN, 20, 4)

class Sphere:
	def __init__(self, stacks=12, slices=24):
		self.vertex_array = []
		self.slices = slices

		stack_interval = pi / stacks
		slice_interval = 2.0 * pi / slices
		self.vertex_count = 0

		for stack_count in range(stacks):
			stack_angle = stack_count * stack_interval

			for slice_count in range(slices + 1):
				slice_angle = slice_count * slice_interval
				self.vertex_array.append(sin(stack_angle) * cos(slice_angle))
				self.vertex_array.append(cos(stack_angle))
				self.vertex_array.append(sin(stack_angle) * sin(slice_angle))

				self.vertex_array.append(sin(stack_angle + stack_interval) * cos(slice_angle))
				self.vertex_array.append(cos(stack_angle + stack_interval))
				self.vertex_array.append(sin(stack_angle + stack_interval) * sin(slice_angle))

				self.vertex_count += 2
		
	def set_vertices(self, shader):
		shader.set_position_attribute(self.vertex_array)
		shader.set_normal_attribute(self.vertex_array)
	
	def draw(self):
		for i in range(0, self.vertex_count, (self.slices + 1) * 2):
			glDrawArrays(GL_TRIANGLE_STRIP, i, (self.slices + 1) * 2)

class Bullet:
	def __init__(self, position, rotation, velocity, damage):
		self.position = position
		self.rotation = rotation
		self.x = position.x
		self.y = position.y
		self.z = position.z
		self.velocity = velocity
		self.damage = damage
		self.speed = 50
	
	def move(self, delta_time):
		self.position += self.velocity * self.speed * delta_time
		self.x += self.velocity.x * self.speed * delta_time
		self.z += self.velocity.z * self.speed * delta_time

class Material:
	def __init__(self, diffuse = None, specular = None, shininess = None):
		self.diffuse = Color(0.0, 0.0, 0.0) if diffuse == None else diffuse
		self.specular = Color(0.0, 0.0, 0.0) if specular == None else specular
		self.shininess = 1 if shininess == None else shininess

class MeshModel:
	def __init__(self):
		self.vertex_arrays = dict()
		# self.index_arrays = dict()
		self.mesh_materials = dict()
		self.materials = dict()
		self.vertex_counts = dict()
		self.vertex_buffer_ids = dict()

	def add_vertex(self, mesh_id, position, normal, uv = None):
		if mesh_id not in self.vertex_arrays:
			self.vertex_arrays[mesh_id] = []
			self.vertex_counts[mesh_id] = 0
		self.vertex_arrays[mesh_id] += [position.x, position.y, position.z, normal.x, normal.y, normal.z]
		self.vertex_counts[mesh_id] += 1

	def set_mesh_material(self, mesh_id, mat_id):
		self.mesh_materials[mesh_id] = mat_id

	def add_material(self, mat_id, mat):
		self.materials[mat_id] = mat

	def set_opengl_buffers(self):
		for mesh_id in self.mesh_materials.keys():
			self.vertex_buffer_ids[mesh_id] = glGenBuffers(1)
			glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_ids[mesh_id])
			glBufferData(GL_ARRAY_BUFFER, numpy.array(self.vertex_arrays[mesh_id], dtype='float32'), GL_STATIC_DRAW)
			glBindBuffer(GL_ARRAY_BUFFER, 0)

	def draw(self, shader):
		for mesh_id, mesh_material in self.mesh_materials.items():
			material = self.materials[mesh_material]
			shader.set_material_diffuse_color(material.diffuse)
			shader.set_material_specular_color(material.specular)
			shader.set_material_shininess(material.shininess)
			shader.set_attribute_buffers(self.vertex_buffer_ids[mesh_id])
			glDrawArrays(GL_TRIANGLES, 0, self.vertex_counts[mesh_id])
			glBindBuffer(GL_ARRAY_BUFFER, 0)