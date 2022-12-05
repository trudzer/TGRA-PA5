from Base3DObjects import *
from Shaders import *
import random

from OpenGL.GL import *

class MazeStruct:
	def __init__(self, x, y, south=True, east=True):
		self.x = x
		self.y = y
		self.south_wall = south
		self.east_wall = east
		self.visited = False
	
	def __str__(self):
		return "[South: %s, East: %s]" % (self.south_wall, self.east_wall)

class Wall:
	def __init__(self, shader, model_matrix, cube, length, pos, color=Vector(1.0, 1.0, 1.0), rotated=False, width=1):
		self.width = width
		self.length = length
		self.rotated = rotated
		self.pos = pos
		self.color = color
		self.shader = shader
		self.model_matrix = model_matrix
		self.cube = cube
		self.height = 5.0
	
	def draw(self):
		self.shader.set_material_diffuse(self.color.x, self.color.y, self.color.z)
		self.shader.set_material_specular(0.0, 0.0, 0.0)

		self.model_matrix.push_matrix()
		
		if self.rotated:
			self.model_matrix.add_translation(self.pos.x - self.length / 2, self.height / 2, self.pos.z - self.width / 2)
			self.model_matrix.add_rotation(0.0, 90.0, 0.0)
		else:
			self.model_matrix.add_translation(self.pos.x - self.width / 2, self.height / 2, self.pos.z - self.length / 2)

		self.model_matrix.add_scale(self.width, self.height, self.length)
		self.shader.set_model_matrix(self.model_matrix.matrix)
		self.cube.draw()
		self.model_matrix.pop_matrix()

class Maze:
	def __init__(self, shader, model_matrix, cube, player_radius, sphere, cell_width=10, grid_size=10):
		self.shader = shader
		self.model_matrix = model_matrix
		self.cube = cube
		self.cell_width = cell_width
		self.grid_size = grid_size
		self.size = self.grid_size * self.cell_width
		self.maze = []
		self.wall_thickness = 1.0
		self.player_radius = player_radius
		self.collision_radius = 0
		self.max_index = self.grid_size - 1
		self.sphere = sphere
		self.end_indices = [x for x in range(5, self.grid_size)]
		self.display_radius = 3
		self.player_row = 0
		self.player_col = 0

		self.create_walls()
	
	def pick_end(self):
		self.end = (random.choice(self.end_indices), random.choice(self.end_indices))
	
	def draw_floor(self, floor_texture):
		if floor_texture:
			self.shader.set_material_diffuse(1.0, 1.0, 1.0)
		else:
			self.shader.set_material_diffuse(0.0, 0.0, 0.0)
		self.shader.set_material_specular(0.0, 0.0, 0.0)
		self.model_matrix.push_matrix()
		self.model_matrix.add_translation(self.size / 2, -0.5, self.size / 2)
		self.model_matrix.add_scale(self.size, 1, self.size)
		self.shader.set_model_matrix(self.model_matrix.matrix)
		self.cube.draw()
		self.model_matrix.pop_matrix()

	def draw_perimeter(self):
		for x in range(self.grid_size):
			if abs(self.player_row - x) < self.display_radius:
				tmp_wall = Wall(self.shader, self.model_matrix, self.cube, self.cell_width, Point(1.0, 1.0, (x + 1) * self.cell_width))
				tmp_wall.draw()

				tmp_wall.pos = Point(self.size, 1.0, (x + 1) * self.cell_width)
				tmp_wall.draw()
		
		for y in range(self.grid_size):
			if abs(self.player_col - y) < self.display_radius:
				tmp_wall = Wall(self.shader, self.model_matrix, self.cube, self.cell_width, Point((y + 1) * self.cell_width, 1.0, 1.0), rotated=True)
				tmp_wall.draw()
				
				tmp_wall.pos = Point((y + 1) * self.cell_width, 1.0, self.size)
				tmp_wall.draw()

	def draw_walls(self):
		for y in range(len(self.maze)):
			for x in range(len(self.maze[y])):
				if abs(self.player_col - x) < self.display_radius and abs(self.player_row - y) < self.display_radius:
					cell = self.maze[y][x]

					if cell.east_wall and x != 0: # Don't draw walls that are outside the perimeter
						tmp_wall = Wall(self.shader, self.model_matrix, self.cube, self.cell_width, Point(x * self.cell_width + self.wall_thickness - 0.0001, 1.0, (y + 1) * self.cell_width))
						tmp_wall.draw()
					if cell.south_wall and y != 0:
						tmp_wall = Wall(self.shader, self.model_matrix, self.cube, self.cell_width, Point((x + 1) * self.cell_width, 1.0, y * self.cell_width + self.wall_thickness - 0.0001), rotated=True)
						tmp_wall.draw()
	
	def set_texture(self, tex, gl_tex, id, diffuse=True):
		if tex != None:
			glActiveTexture(gl_tex)
			glBindTexture(GL_TEXTURE_2D, tex)

			if diffuse:
				self.shader.set_diffuse_texture(id)
			else:
				self.shader.set_normal_map_texture(id)

	def unset_texture(self, tex, gl_tex, diffuse=True):
		if tex != None:
			glActiveTexture(gl_tex)
			glBindTexture(GL_TEXTURE_2D, 0)

			if diffuse:
				self.shader.set_use_diffuse_texture(False)
			else:
				self.shader.set_use_normal_texture(False)

	def draw(self, wall_texture=None, wall_normal=None, floor_texture=None, floor_normal=None):
		self.cube.set_vertices(self.shader)
		self.shader.set_model_matrix(self.model_matrix.matrix)

		self.set_texture(wall_texture, GL_TEXTURE1, 1)
		self.set_texture(wall_normal, GL_TEXTURE3, 3, False)
		self.draw_perimeter()
		self.draw_walls()
		self.unset_texture(wall_texture, GL_TEXTURE1)
		self.unset_texture(wall_normal, GL_TEXTURE3, False)
		
		self.shader.set_light_position(Point(self.grid_size / 2 * self.cell_width, 1000.0, self.grid_size / 2 * self.cell_width))
		
		self.set_texture(floor_texture, GL_TEXTURE1, 1)
		self.set_texture(floor_normal, GL_TEXTURE3, 3, False)
		self.draw_floor(floor_texture)
		self.unset_texture(floor_texture, GL_TEXTURE1)
		self.unset_texture(floor_normal, GL_TEXTURE3, False)

	def create_path(self, visited, x, y, num_visited, total_cells):
		if num_visited >= total_cells - 1:
			return
		
		if not self.maze[y][x].visited:
			visited.append(self.maze[y][x])
			self.maze[y][x].visited = True

		available = []

		if x > 0 and not self.maze[y][x - 1].visited:
			available.append((y, x - 1, "E"))
		if x < self.max_index and not self.maze[y][x + 1].visited:
			available.append((y, x + 1, "W"))
		if y > 0 and not self.maze[y - 1][x].visited:
			available.append((y - 1, x, "S"))
		if y < self.max_index and not self.maze[y + 1][x].visited:
			available.append((y + 1, x, "N"))
		
		if len(available) == 0:
			cell = visited.pop()
			return self.create_path(visited, cell.x, cell.y, num_visited, total_cells)
		
		pick = random.choice(available)

		if pick[2] == "S":
			self.maze[y][x].south_wall = False
		elif pick[2] == "N":
			self.maze[y + 1][x].south_wall = False
		elif pick[2] == "E":
			self.maze[y][x].east_wall = False
		elif pick[2] == "W":
			self.maze[y][x + 1].east_wall = False

		return self.create_path(visited, pick[1], pick[0], num_visited + 1, total_cells)

	def create_walls(self):
		self.maze = [[MazeStruct(x, y) for x in range(self.grid_size)] for y in range(self.grid_size)]
		
		self.create_path([], 0, 0, 0, self.grid_size ** 2)
	
	def hit_edge(self, vel, new_pos):
		# Edge collision x
		if vel.x < 0.0:
			if new_pos.x - self.collision_radius - self.wall_thickness < 0.0:
				vel.x = 0.0
		elif vel.x > 0.0:
			if new_pos.x + self.collision_radius + self.wall_thickness > self.size:
				vel.x = 0.0
		
		# Edge collision y
		if vel.z < 0.0:
			if new_pos.z - self.collision_radius - self.wall_thickness < 0.0:
				vel.z = 0.0
		elif vel.z > 0.0:
			if new_pos.z + self.collision_radius + self.wall_thickness > self.size:
				vel.z = 0.0
		
		return vel
	
	def check_hit_edge(self, vel, new_pos):
		# Edge collision x
		if vel.x < 0.0:
			if new_pos.x - self.collision_radius - self.wall_thickness < 0.0:
				return True
		elif vel.x > 0.0:
			if new_pos.x + self.collision_radius + self.wall_thickness > self.size:
				return True
		
		# Edge collision y
		if vel.z < 0.0:
			if new_pos.z - self.collision_radius - self.wall_thickness < 0.0:
				return True
		elif vel.z > 0.0:
			if new_pos.z + self.collision_radius + self.wall_thickness > self.size:
				return True
		
		return False
	
	def hit_x(self, new_pos, row, bias=0):
		player_z_min = new_pos.z - self.collision_radius
		player_z_max = new_pos.z + self.collision_radius + self.wall_thickness
		wall_z_min = row * self.cell_width + bias
		wall_z_max = wall_z_min + self.wall_thickness

		if (player_z_max > wall_z_min or player_z_min > wall_z_min) and (player_z_max < wall_z_max or player_z_min < wall_z_max):
			return True
		
		return False
	
	def hit_z(self, new_pos, col, bias=0):
		player_x_min = new_pos.x - self.collision_radius
		player_x_max = new_pos.x + self.collision_radius + self.wall_thickness
		wall_x_min = col * self.cell_width + bias
		wall_x_max = wall_x_min + self.wall_thickness

		if (player_x_max > wall_x_min or player_x_min > wall_x_min) and (player_x_max < wall_x_max or player_x_min < wall_x_max):
			return True
		
		return False

	def collision_west(self, new_pos, player_row, player_col):
		if player_col + 1 <= self.max_index:
			cell_west = self.maze[player_row][player_col + 1]
			cell_south_west = self.maze[player_row - 1][player_col + 1]
			cell_north_west = None
			
			if player_row + 1 <= self.max_index:
				cell_north_west = self.maze[player_row + 1][player_col + 1]
			
			player_x_max = new_pos.x + self.collision_radius + self.wall_thickness + 0.1
			wall_x_max = (player_col + 1) * self.cell_width + self.wall_thickness

			if player_x_max > wall_x_max:
				if cell_west.east_wall:
					return True
				if cell_north_west != None:
					if cell_north_west.east_wall or cell_north_west.south_wall:
						if self.hit_x(new_pos, player_row + 1, self.wall_thickness):
							return True
				if cell_south_west.east_wall:
					if self.hit_x(new_pos, player_row, -self.wall_thickness):
						return True
				if cell_west.south_wall:
					if self.hit_x(new_pos, player_row):
						return True
	
	def collision_east(self, new_pos, player_row, player_col):
		cell = self.maze[player_row][player_col]
		cell_south = self.maze[player_row - 1][player_col]
		cell_east = self.maze[player_row][player_col - 1]
		cell_north_east = None
		cell_north = None
		
		if player_row + 1 <= self.max_index:
			cell_north = self.maze[player_row + 1][player_col]
			cell_north_east = self.maze[player_row + 1][player_col - 1]
		
		player_x_min = new_pos.x - self.collision_radius - 0.1
		wall_x_max = player_col * self.cell_width + self.wall_thickness
		wall_x_min = player_col * self.cell_width

		if player_x_min < wall_x_max:
			if cell.east_wall:
				return True
			if cell_north != None:
				if cell_north.east_wall:
					if self.hit_x(new_pos, player_row + 1, self.wall_thickness):
						return True
			if cell_south.east_wall:
				if self.hit_x(new_pos, player_row, -self.wall_thickness):
					return True
		if player_x_min < wall_x_min:
			if cell_east.south_wall:
				if self.hit_x(new_pos, player_row):
					return True
			if cell_north_east != None:
				if cell_north_east.south_wall:
					if self.hit_x(new_pos, player_row + 1, self.wall_thickness):
						return True

	def collision_north(self, new_pos, player_row, player_col):
		if player_row + 1 <= self.max_index:
			cell_north = self.maze[player_row + 1][player_col]
			cell_north_east = self.maze[player_row + 1][player_col - 1]
			cell_north_west = None

			if player_col + 1 <= self.max_index:
				cell_north_west = self.maze[player_row + 1][player_col + 1]

			player_z_max = new_pos.z + self.collision_radius + self.wall_thickness + 0.1
			wall_z_max = (player_row + 1) * self.cell_width + self.wall_thickness

			if player_z_max > wall_z_max:
				if cell_north.south_wall:
					return True
				if cell_north_east.south_wall:
					if self.hit_z(new_pos, player_col, -self.wall_thickness):
						return True
				if cell_north_west != None:
					if cell_north_west.south_wall or cell_north_west.east_wall:
						if self.hit_z(new_pos, player_col + 1, self.wall_thickness):
							return True
				if cell_north.east_wall:
					if self.hit_z(new_pos, player_col):
						return True
	
	def collision_south(self, new_pos, player_row, player_col):
		cell = self.maze[player_row][player_col]
		cell_east = self.maze[player_row][player_col - 1]
		cell_south = self.maze[player_row - 1][player_col]
		cell_west = None
		cell_south_west = None

		if player_col + 1 <= self.max_index:
			cell_west = self.maze[player_row][player_col + 1]
			cell_south_west = self.maze[player_row - 1][player_col + 1]

		player_z_min = new_pos.z - self.collision_radius - 0.1
		wall_z_max = player_row * self.cell_width + self.wall_thickness
		wall_z_min = wall_z_max - self.wall_thickness

		if player_z_min < wall_z_max:
			if cell.south_wall:
				return True
			if cell_west != None:
				if cell_west.south_wall:
					if self.hit_z(new_pos, player_col + 1, self.wall_thickness):
						return True
			if cell_east.south_wall:
				if self.hit_z(new_pos, player_col, -self.wall_thickness):
					return True
		if player_z_min < wall_z_min:
			if cell_south.east_wall:
				if self.hit_z(new_pos, player_col):
					return True
			if cell_south_west != None:
				if cell_south_west.east_wall:
					if self.hit_z(new_pos, player_col + 1, self.wall_thickness):
						return True

	def collide(self, pos, vel, radius=None, just_check=False):
		if radius == None:
			self.collision_radius = self.player_radius
		else:
			self.collision_radius = radius

		new_pos = pos + vel

		if just_check:
			if self.check_hit_edge(vel, new_pos):
				return True
		
		new_vel = self.hit_edge(vel, new_pos)

		player_row = int(pos.z / self.cell_width)
		player_col = int(pos.x / self.cell_width)

		self.player_row = player_row
		self.player_col = player_col

		hit_x = False
		hit_z = False

		# Maze wall collision
		if new_vel.x > 0.0: # Player moving west
			hit_x = self.collision_west(new_pos, player_row, player_col)
		elif new_vel.x < 0.0: # Player moving east
			hit_x = self.collision_east(new_pos, player_row, player_col)
		
		if new_vel.z > 0.0:
			hit_z = self.collision_north(new_pos, player_row, player_col)
		elif new_vel.z < 0.0:
			hit_z = self.collision_south(new_pos, player_row, player_col)
		
		if just_check:
			if hit_x or hit_z:
				return True
			else:
				return False

		if hit_x:
			new_vel.x = 0.0
		
		if hit_z:
			new_vel.z = 0.0

		return new_vel