from Matrices import *
from Base3DObjects import *
from math import *

from Helpers import look_at

class Enemy:
	def __init__(self, maze, model_matrix, pos, obj, health=100, collision_radius=2, speed=10, hit_cooldown=1, damage=25, health_bar_offset=4, scale_factor=1.0):
		self.maze = maze
		self.model_matrix = model_matrix
		self.pos = pos
		self.y = pos.y
		self.vel = Vector(0, 0, 0)
		self.max_health = health
		self.health = health
		self.rotation = 0
		self.cube = Cube()
		self.radius = maze.cell_width * 1.5
		self.obj = obj
		self.collision_radius = collision_radius
		self.speed = speed
		self.last_known_hit = 1000
		self.hit_cooldown = hit_cooldown
		self.damage = damage
		self.health_bar_offset = health_bar_offset
		self.scale_factor = scale_factor
		self.alive = True
		self.dist = 0

	def update(self, delta_time, player_pos):
		if self.health <= 0:
			self.alive = False
			return
		
		self.last_known_hit += delta_time
		dist_vec = player_pos - self.pos
		self.dist = self.get_distance_to(player_pos)
		
		self.rotation = look_at(self.pos, player_pos, pi / 2)
		
		dist = self.get_distance_to(player_pos)
		if dist <= self.radius and dist > self.collision_radius - 0.1:
			dist_vec.normalize()
			self.vel = dist_vec * self.speed * delta_time
			self.vel = self.maze.collide(self.pos, self.vel, radius=self.collision_radius)
			self.pos += self.vel

	def get_distance_to(self, other):
		return (other - self.pos).__len__()

	def draw(self, shader):
		if not self.alive:
			return
		
		self.model_matrix.push_matrix()
		self.model_matrix.add_translation(self.pos.x, self.y, self.pos.z)
		self.model_matrix.add_rotation_y(-self.rotation)
		self.model_matrix.add_scale(self.scale_factor, self.scale_factor, self.scale_factor)
		shader.set_model_matrix(self.model_matrix.matrix)
		self.obj.draw(shader)
		self.model_matrix.pop_matrix()

		### DRAW CUBE ABOVE ENEMY FOR HEALTH BAR ###
		self.model_matrix.push_matrix()
		self.model_matrix.add_translation(self.pos.x, self.y + self.health_bar_offset, self.pos.z)
		self.model_matrix.add_rotation_y(-self.rotation)
		self.model_matrix.add_scale(0.5, 0.5, (self.health / self.max_health) * 4)
		shader.set_material_diffuse(1.0, 0.1, 0.1)
		shader.set_model_matrix(self.model_matrix.matrix)
		self.cube.set_vertices(shader)
		self.cube.draw()
		self.model_matrix.pop_matrix()
	
	def draw_minimap(self, shader):
		if not self.alive:
			return
		
		self.cube.set_vertices(shader)
		shader.set_material_diffuse(0.9, 0.1, 0.1)
		self.model_matrix.push_matrix()
		self.model_matrix.add_translation(self.pos.x, 1, self.pos.z)
		shader.set_model_matrix(self.model_matrix.matrix)
		self.cube.set_vertices(shader)
		self.cube.draw()
		self.model_matrix.pop_matrix()