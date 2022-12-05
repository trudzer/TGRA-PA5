from math import *
from random import choice

import pygame
from pygame.locals import *

import pyglet.gl

from Shaders import *
from Matrices import *
from Maze import *
from Entities import *

import obj_3D_loading

from Helpers import look_at

class GraphicsProgram3D:
	def __init__(self):
		self.init_pygame()
		self.init_variables()
		self.init_matrices()
		self.init_shooting_vars()
		self.init_input()
		self.init_shaders()
		self.init_textures()
		self.init_cameras()
		self.init_objects()
		self.init_opengl()

	def init_shaders(self):
		self.shader = Shader3D()
		self.shader_td = Shader3D()

		self.shader_td.use()
		self.shader_td.set_light_specular(0.0, 0.0, 0.0)
		self.shader_td.set_material_specular(0.0, 0.0, 0.0)
		self.shader_td.set_material_shininess(0)

		self.shader.use()
	
	def init_input(self):
		self.speed = 12.0

		self.W_key_down = False
		self.A_key_down = False
		self.S_key_down = False
		self.D_key_down = False
		self.TAB_key_down = False
		self.R_key_down = False

	def init_top_down(self):
		self.td_width = 200
		self.td_height = 200
		self.td_ratio = 10
		self.td_left = -self.td_width / self.td_ratio
		self.td_right = self.td_width / self.td_ratio
		self.td_bottom = -self.td_height / self.td_ratio
		self.td_top = self.td_height / self.td_ratio
		self.td_x = 0
		self.td_y = self.height - self.td_height

	def init_variables(self):
		self.fov = pi / 3
		self.aspect = self.width / self.height
		self.near = 0.1
		self.far = 90
		self.player_start = Point(5, 2, 5)
		self.player_look_start = Point(10, 2, 5)
		self.player_rot = Vector(0, 0, 0)
		self.up = Vector(0, 1, 0)
		self.angle = 0
		self.clear_color = 0.1
		self.health = 100
		self.bullet_damage = 25
		self.last_hit = 0.0
		self.regen_start = 3
		self.regen_interval = 0.5
		self.regen_amount = 3
		self.last_regen = self.regen_interval
		self.player_radius = 1.55
		self.num_enemies = 30
		self.enemy_health = 100
		self.boss_health = 750 # Increased by 250 every time the player beats a level, including the first level so this will start at 1000
		self.boss_figth = False
		self.mouse_x = 0
		self.gun_rotation = 0
		self.gun_reload_rotation = 0
		
		self.init_top_down()
	
	def init_pygame(self):
		pygame.init()
		display_info = pygame.display.Info() 
		self.width = display_info.current_w
		self.height = display_info.current_h
		pygame.display.set_mode((self.width, self.height), pygame.OPENGL|pygame.DOUBLEBUF)
		pygame.mouse.set_visible(False)
		pygame.event.set_grab(True)

		self.clock = pygame.time.Clock()
		self.clock.tick()

	def init_cameras(self):
		self.fp_camera = Camera()
		self.fp_camera.look(self.player_start, self.player_look_start, self.up)
		self.td_camera = Camera()
	
	def init_matrices(self):
		self.model_matrix = ModelMatrix()
		self.projection_matrix = ProjectionMatrix()
		self.projection_matrix.set_perspective(self.fov, self.aspect, self.near, self.far)

	def init_enemies(self):
		min_cell = 1
		max_cell = 10
		available_cells = [[x, y] for y in range(min_cell, max_cell + 1) for x in range(min_cell, max_cell + 1)]
		available_cells.pop(available_cells.index([1, 1]))
		available_cells.pop(available_cells.index([1, 2]))
		available_cells.pop(available_cells.index([2, 1]))
		available_cells.pop(available_cells.index([2, 2]))
		cell_width = self.maze.cell_width

		self.enemies = []

		for _ in range(self.num_enemies):
			if len(available_cells) == 0:
				break
			
			# Pick a random row an column from the available ones
			cell = choice(available_cells)

			# Remove the picked row and column from the available ones
			available_cells.pop(available_cells.index(cell))

			# Create the enemy and put them in the enemy list
			tmp_enemy = Enemy(self.maze, self.model_matrix, Point(cell[0] * cell_width - cell_width / 2, 0, cell[1] * cell_width - cell_width / 2), self.obj_enemy, health=self.enemy_health, speed=8)
			tmp_enemy.dist = tmp_enemy.get_distance_to(self.fp_camera.eye)
			self.enemies.append(tmp_enemy)
	
	def init_objects(self):
		self.cube = Cube()
		self.sphere = Sphere()
		self.obj_enemy = obj_3D_loading.load_obj_file("models", "enemy.obj")
		self.obj_gun = obj_3D_loading.load_obj_file("models", "gun.obj")
		self.obj_boss = obj_3D_loading.load_obj_file("models", "bigboss.obj")
		self.sound_main_theme = pyglet.media.load("sounds/maintheme.mp3", streaming=False)
		self.sound_shoot = pyglet.media.load("sounds/shoot.wav", streaming=False)
		self.sound_reload = pyglet.media.load("sounds/reload.wav", streaming=False)
		self.sound_shoot.volume = 0.5
		self.sound_shoot.loop = False
		self.sound_reload.volume = 0.4
		self.sound_reload.loop = False
		self.sound_main_theme.loop = True
		self.sound_main_theme.play()
		self.generate_maze()

	def init_opengl(self):
		glEnable(GL_DEPTH_TEST)
		glEnable(GL_SCISSOR_TEST) # For multiple viewports
	
	def init_shooting_vars(self):
		self.shooting = False
		self.fire_rate = 800 / 60
		self.last_known_fired = 0
		self.shots_fired = 0
		self.bullet_list = []
		self.bullet_scale = 0.03
		self.reload_time = 1.7
		self.reloading = False
	
	def init_textures(self):
		self.textures_folder = "textures/"
		self.wall_texture = self.load_texture("brickwall.png")
		self.wall_normal_map = self.load_texture("brickwall_normal.png")
		self.floor_texture = self.load_texture("floor.png")
		self.floor_normal_map = self.load_texture("floor_normal.png")

	def load_texture(self, path_string):
		surface = pygame.image.load(self.textures_folder + path_string)
		tex_string = pygame.image.tostring(surface, "RGBA", 1)
		width = surface.get_width()
		height = surface.get_height()
		tex_id = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, tex_id)
		
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

		glTexImage2D(GL_TEXTURE_2D, 0, GL_SRGB_ALPHA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_string)
		return tex_id

	def generate_maze(self):
		self.boss_figth = False

		maze_cell_width = 10
		maze_grid_size = 10
		maze_cube = Cube(maze_cell_width)

		self.maze = Maze(self.shader, self.model_matrix, maze_cube, self.player_radius, self.sphere, maze_cell_width, maze_grid_size)
	
		self.far = maze_cell_width * (self.maze.display_radius - 1)

		self.shader.set_fog_min_distance(maze_cell_width * (self.maze.display_radius - 1.5))
		self.shader.set_fog_max_distance(self.far)

		self.init_enemies()

	def generate_boss_maze(self):
		self.boss_figth = True

		boss_maze_cell_width = 20
		boss_maze_grid_size = 5
		boss_maze_cube = Cube(boss_maze_cell_width)
		boss_radius = 2
		
		self.maze = Maze(self.shader, self.model_matrix, boss_maze_cube, self.player_radius, self.sphere, boss_maze_cell_width, boss_maze_grid_size)

		self.far = boss_maze_cell_width * (self.maze.display_radius - 1)

		self.shader.set_fog_min_distance(boss_maze_cell_width * (self.maze.display_radius - 1.5))
		self.shader.set_fog_max_distance(self.far)

		boss_location = boss_maze_cell_width * boss_maze_grid_size / 2 - boss_maze_cell_width

		self.enemies = [
			Enemy(self.maze, self.model_matrix, Point(boss_location, 0, boss_location), self.obj_boss, health=self.boss_health, collision_radius=boss_radius, speed=6, hit_cooldown=2, damage=50, health_bar_offset=6)
		]

		for i in range(ceil(self.num_enemies / 3)):
			self.enemies.append(Enemy(self.maze, self.model_matrix, Point(boss_location + (random() - 0.5) * 16, 0, boss_location + (random() - 0.5) * 16), self.obj_enemy, health=self.enemy_health, speed=8))

	def increase_difficulty(self):
		if self.boss_figth:
			self.num_enemies += 2
			self.enemy_health += self.bullet_damage
		else:
			self.boss_health += 250

	def reset(self):
		self.fp_camera.eye = self.player_start
		self.fp_camera.look(self.fp_camera.eye, self.player_look_start, self.up)
		self.health = 100
		self.last_hit = 0.0
		self.enemies_killed = 0
		
		if self.boss_figth:
			self.generate_maze()
		else:
			self.generate_boss_maze()
		
		self.init_shooting_vars()

	def reload_gun(self):
		self.sound_reload.play()
		self.shots_fired = 30
		self.shooting = False
		self.last_known_fired = -self.reload_time
		self.reloading = True

	def update_bullets(self, delta_time):
		self.last_known_fired += delta_time
		
		if self.shooting:
			if self.last_known_fired > 1.0 / self.fire_rate:
				self.shots_fired += 1
				bullet_pos = Point(self.fp_camera.eye.x, self.fp_camera.eye.y - 0.3, self.fp_camera.eye.z) + self.fp_camera.get_velocity(Vector(0, 0, -2))
				bullet_look_pos = bullet_pos + self.fp_camera.get_velocity(Vector(0, 0, -1))
				bullet_vel = self.fp_camera.get_velocity(Vector(0, 0, -1))
				bullet = Bullet(bullet_pos, look_at(bullet_pos, bullet_look_pos), bullet_vel, self.bullet_damage)
				self.bullet_list.append(bullet)
				self.last_known_fired = 0.0
				self.sound_shoot.play()
		
		if self.reloading:
			if self.last_known_fired > 0:
				self.shots_fired = 0
				self.reloading = False

		if (self.shots_fired >= 30 or (self.R_key_down and self.shots_fired > 0)) and not self.reloading:
			self.reload_gun()
		
		if len(self.bullet_list) > 30:
			self.bullet_list.pop(0)
		
		index = 0
		bullets_to_remove = []
		for b in self.bullet_list:
			enemies_to_remove = []
			hit = self.maze.collide(Point(b.x, b.y, b.z), b.velocity, self.bullet_scale, True)
			enemy_index = 0
			for e in self.enemies:
				if (b.position - e.pos).__len__() < e.collision_radius:
					e.health -= b.damage
					
					if e.health <= 0:
						self.enemies[enemy_index].alive = False
						enemies_to_remove.append(enemy_index)
					
					hit = True
				enemy_index += 1
			
			if len(enemies_to_remove) > 0:
				for e in enemies_to_remove[::-1]:
					self.enemies.pop(e)

				print(f"Remaining enemies: {len(self.enemies)}")
				
				if len(self.enemies) == 0:
					self.increase_difficulty()
					self.reset()

			if hit:
				bullets_to_remove.append(index)
			else:
				b.move(delta_time)
			index += 1

		if len(bullets_to_remove) > 0 and len(self.bullet_list) > 0:
			for b in bullets_to_remove[::-1]:
				try:
					self.bullet_list.pop(b)
				except:
					pass

	def check_enemy(self, enemy, calc_dist=False):
		if enemy == None:
			return False
		
		if not enemy.alive:
			return False
		
		if calc_dist:
			enemy.dist = enemy.get_distance_to(self.fp_camera.eye)
		
		if enemy.dist > self.far:
			return False

		return True

	def update_enemies(self, delta_time):
		for e in self.enemies:
			if not self.check_enemy(e, True):
				continue
			
			#e.dist = e.get_distance_to(self.fp_camera.eye)
			
			e.update(delta_time, self.fp_camera.eye)
			if e.dist < e.collision_radius and e.last_known_hit > e.hit_cooldown:
				e.last_known_hit = 0.0
				self.health -= e.damage
				self.last_hit = 0.0

				if self.health <= 0:
					self.boss_figth = not self.boss_figth
					self.reset()

	def update(self):
		delta_time = self.clock.tick() / 1000.0
		mouse_movement = pygame.mouse.get_rel()
		player_velocity = Vector(0, 0, 0)

		pygame.display.set_caption(f'{self.clock.get_fps() :.1f}')

		self.angle += pi * delta_time
		if self.angle > 2 * pi:
			self.angle -= (2 * pi)

		if self.W_key_down:
			player_velocity.z -= self.speed * delta_time
		if self.A_key_down:
			player_velocity.x -= self.speed * delta_time
		if self.S_key_down:
			player_velocity.z += self.speed * delta_time
		if self.D_key_down:
			player_velocity.x += self.speed * delta_time
		
		self.shooting = pygame.mouse.get_pressed()[0]
		
		self.last_hit += delta_time
		if self.health < 100:
			if self.last_hit > self.regen_start:
				self.last_regen += delta_time
				if self.last_regen > self.regen_interval:
					self.last_regen = 0.0
					self.health += self.regen_amount
					if self.health > 100:
						self.health = 100

		# Enemy update
		self.update_enemies(delta_time)

		self.update_bullets(delta_time)

		new_vel = self.maze.collide(self.fp_camera.eye, self.fp_camera.get_velocity(player_velocity))
		if new_vel == None:
			self.fp_camera.eye = self.player_start
		else:
			self.fp_camera.move(new_vel)

		# Use mouse movement to look around
		if self.reloading:
			self.gun_reload_rotation = sin(((-self.last_known_fired / self.reload_time) * 2) * pi / 2)
		
		if abs(self.gun_rotation) > pi / 2:
			self.gun_rotation = self.gun_rotation % (pi / 2)
		
		buffer = 1
		if self.gun_rotation < -buffer:
			self.gun_rotation += delta_time * 75
		elif self.gun_rotation > buffer:
			self.gun_rotation -= delta_time * 75
		else:
			self.gun_rotation = 0
		
		self.mouse_x = -mouse_movement[0]
		self.gun_rotation += self.mouse_x * delta_time * 10
		self.fp_camera.yaw(self.mouse_x * 0.1 * delta_time)

	def draw_cube(self, x, y, z, scale):
		self.shader.set_use_diffuse_texture(False)
		self.model_matrix.push_matrix()
		self.model_matrix.add_translation(x, y, z)
		self.model_matrix.add_scale(scale, scale, scale)
		self.shader.set_model_matrix(self.model_matrix.matrix)
		self.cube.draw()
		self.model_matrix.pop_matrix()

	def draw_bullets(self):
		for i in self.bullet_list:
			self.shader.set_material_diffuse(0.8, 0.5, 0.2)
			self.model_matrix.push_matrix()
			self.model_matrix.add_translation(i.x, i.y, i.z)
			self.model_matrix.add_rotation_y(i.rotation)
			self.model_matrix.add_scale(self.bullet_scale, self.bullet_scale, self.bullet_scale)
			self.shader.set_model_matrix(self.model_matrix.matrix)
			self.cube.set_vertices(self.shader)
			self.cube.draw()
			self.model_matrix.pop_matrix()

	def draw_minimap(self):
		if not self.TAB_key_down:
			glViewport(self.td_x, self.td_y, self.td_width, self.td_height)
			glScissor(self.td_x, self.td_y, self.td_width, self.td_height)
		
		clear_color = 0.0
		glClearColor(clear_color, clear_color, clear_color, 1.0)
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
		
		n = self.fp_camera.n
		rotation = Vector(-n.x, -n.y, -n.z)
		eye = Point(self.fp_camera.eye.x, 10.0, self.fp_camera.eye.z)
		self.td_camera.look(eye, self.fp_camera.eye, rotation)

		self.shader_td.use()

		self.shader_td.set_light_specular(0.0, 0.0, 0.0)
		self.shader_td.set_material_specular(0.0, 0.0, 0.0)
		self.shader_td.set_material_shininess(0)

		self.shader_td.set_eye_position(self.td_camera.eye)
		self.shader_td.set_light_position(self.td_camera.eye)

		self.shader_td.set_light_diffuse(1.0, 1.0, 1.0)
		self.shader_td.set_use_fog(False)

		self.shader_td.set_player_health(100)
		
		self.projection_matrix.set_orthographic(self.td_left, self.td_right, self.td_bottom, self.td_top, self.near, self.far)
		self.shader_td.set_projection_matrix(self.projection_matrix.get_matrix())

		self.shader_td.set_view_matrix(self.td_camera.get_matrix())

		self.model_matrix.load_identity()

		self.cube.set_vertices(self.shader_td)
		self.shader_td.set_material_diffuse(0.1, 0.9, 0.1)
		self.model_matrix.push_matrix()
		self.model_matrix.add_translation(eye.x, 2.5, eye.z)
		self.shader_td.set_model_matrix(self.model_matrix.matrix)
		self.cube.draw()
		self.model_matrix.pop_matrix()

		# Draw the maze on the minimap
		self.maze.draw()

		for b in self.bullet_list:
			self.shader.set_material_diffuse(0.3, 0.3, 0.1)
			self.draw_cube(b.x, 2.0, b.z, 0.3)

		for e in self.enemies:
			if self.check_enemy(e):
				e.draw_minimap(self.shader_td)

	def draw_first_person(self):
		glViewport(0, 0, self.width, self.height)
		glScissor(0, 0, self.width, self.height)
		glClearColor(0, 0, 0, 1.0)
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
		
		self.shader.use()
		
		self.projection_matrix.set_perspective(self.fov, self.aspect, self.near, self.far)
		self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

		self.shader.set_light_diffuse(1.0, 1.0, 1.0)
		self.shader.set_light_specular(1.0, 1.0, 1.0)

		self.shader.set_view_matrix(self.fp_camera.get_matrix())

		self.shader.set_eye_position(self.fp_camera.eye)
		self.shader.set_light_position(self.fp_camera.eye)

		self.shader.set_use_fog(True)
		self.shader.set_player_health(self.health)

		### DRAW BULLETS ###
		self.draw_bullets()

		### DRAW MAZE ###
		self.maze.draw(wall_texture=self.wall_texture, wall_normal=self.wall_normal_map, floor_texture=self.floor_texture, floor_normal=self.floor_normal_map)
		
		### DRAW GUN ###
		self.shader.set_light_position(Point(self.fp_camera.eye.x, 4, self.fp_camera.eye.z))

		self.model_matrix.push_matrix()

		gun_pos = self.fp_camera.get_velocity(Vector(0, -0.3, -1)) + self.fp_camera.eye
		look_point = self.fp_camera.get_velocity(Vector(0, -0.3, -2)) + self.fp_camera.eye
		self.model_matrix.add_translation(gun_pos.x, gun_pos.y, gun_pos.z)
		self.model_matrix.add_rotation_y(-look_at(gun_pos, look_point, -pi / 2))
		self.model_matrix.add_rotation_x(-self.gun_rotation * 0.01)

		if self.reloading:
			move = self.fp_camera.get_velocity(Vector(0, -self.gun_reload_rotation, 0))
			self.model_matrix.add_translation(move.x, move.y, move.z)
		
		gun_scale = 0.7
		self.model_matrix.add_scale(gun_scale, gun_scale, gun_scale)
		self.shader.set_model_matrix(self.model_matrix.matrix)
		self.obj_gun.draw(self.shader)

		self.model_matrix.pop_matrix()
		
		### DRAW ENEMIES ###
		for e in self.enemies:
			if self.check_enemy(e):
				try:
					e.draw(self.shader)
				except:
					print(e.obj)

	def draw_ui(self):
		border_width = 5
		element_height = 25

		### DRAW HEALTH BAR ###
		healthbar_width = int(self.health * 4.45)
		glViewport(self.width - healthbar_width - border_width, border_width, healthbar_width, element_height)
		glScissor(self.width - healthbar_width - border_width, border_width, healthbar_width, element_height)
		glClearColor(1.0, 0.0, 0.0, 1.0)
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

		### DRAW REMAINING BULLETS ###
		bullet_width = 10

		glClearColor(0.7, 0.65, 0.1, 1.0)
		for i in range(30 - self.shots_fired):
			bullet_offset = border_width * (i + 1) + bullet_width * i
			glViewport(bullet_offset, border_width, bullet_width, element_height)
			glScissor(bullet_offset, border_width, bullet_width, element_height)
			glClear(GL_COLOR_BUFFER_BIT)
		
		### DRAW RELOAD PROGRESS BAR ###
		glClearColor(0.1, 0.1, 0.5, 1.0)
		if self.reloading:
			reload_bar_max_length = 445 # 445 pixels is equal to the width of the 30 bullets
			reload_bar_width = int((1 - (abs(self.last_known_fired) / self.reload_time)) * reload_bar_max_length)
			glViewport(border_width, border_width, reload_bar_width, element_height)
			glScissor(border_width, border_width, reload_bar_width, element_height)
			glClear(GL_COLOR_BUFFER_BIT)
		
		### DRAW ENEMIES
		glClearColor(1.0, 0.1, 0.1, 1.0)
		enemy_width = 10
		enemy_num = 0
		for i in range(len(self.enemies)):
			enemy = self.enemies[i]
			if enemy == None:
				continue
			
			if enemy.alive:
				enemy_offset = border_width * (enemy_num + 1) + enemy_width * enemy_num
				glViewport(self.width - enemy_offset - border_width, self.height - element_height - border_width, enemy_width, element_height)
				glScissor(self.width - enemy_offset - border_width, self.height - element_height - border_width, enemy_width, element_height)
				glClear(GL_COLOR_BUFFER_BIT)
				enemy_num += 1

	def draw(self):
		self.draw_first_person()
		self.draw_minimap()
		self.draw_ui()
		
		pygame.display.flip()

	def program_loop(self):
		exiting = False
		while not exiting:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					print("Quitting!")
					exiting = True
				elif event.type == pygame.KEYDOWN:
					if event.key == K_ESCAPE:
						print("Escaping!")
						exiting = True
					if event.key == K_w:
						self.W_key_down = True
					if event.key == K_a:
						self.A_key_down = True
					if event.key == K_s:
						self.S_key_down = True
					if event.key == K_d:
						self.D_key_down = True
					if event.key == K_TAB:
						self.TAB_key_down = not self.TAB_key_down
					if event.key == K_r:
						self.R_key_down = True
					### CHEATCODE FOR TESTING
					# if event.key == K_SPACE:
					# 	self.increase_difficulty()
					# 	self.reset()
				elif event.type == pygame.KEYUP:
					if event.key == K_w:
						self.W_key_down = False
					if event.key == K_a:
						self.A_key_down = False
					if event.key == K_s:
						self.S_key_down = False
					if event.key == K_d:
						self.D_key_down = False
					if event.key == K_r:
						self.R_key_down = False
			
			self.update()
			self.draw()

		#OUT OF GAME LOOP
		pygame.quit()

	def start(self):
		self.program_loop()

if __name__ == "__main__":
	GraphicsProgram3D().start()