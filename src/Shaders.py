from OpenGL.GL import *
from OpenGL.GLU import *
from math import * # trigonometry

import sys

from Base3DObjects import *

class Shader3D:
	def __init__(self):
		vert_shader = glCreateShader(GL_VERTEX_SHADER)
		shader_file = open("simple3D.vert")
		glShaderSource(vert_shader,shader_file.read())
		shader_file.close()
		glCompileShader(vert_shader)
		result = glGetShaderiv(vert_shader, GL_COMPILE_STATUS)
		if (result != 1): # shader didn't compile
			print("Couldn't compile vertex shader\nShader compilation Log:\n" + str(glGetShaderInfoLog(vert_shader)))

		frag_shader = glCreateShader(GL_FRAGMENT_SHADER)
		shader_file = open("simple3D.frag")
		glShaderSource(frag_shader,shader_file.read())
		shader_file.close()
		glCompileShader(frag_shader)
		result = glGetShaderiv(frag_shader, GL_COMPILE_STATUS)
		if (result != 1): # shader didn't compile
			print("Couldn't compile fragment shader\nShader compilation Log:\n" + str(glGetShaderInfoLog(frag_shader)))

		self.renderingProgramID = glCreateProgram()
		glAttachShader(self.renderingProgramID, vert_shader)
		glAttachShader(self.renderingProgramID, frag_shader)
		glLinkProgram(self.renderingProgramID)

		self.positionLoc = glGetAttribLocation(self.renderingProgramID, "a_position")
		glEnableVertexAttribArray(self.positionLoc)

		self.normalLoc = glGetAttribLocation(self.renderingProgramID, "a_normal")
		glEnableVertexAttribArray(self.normalLoc)

		self.uvLoc = glGetAttribLocation(self.renderingProgramID, "a_uv")
		glEnableVertexAttribArray(self.uvLoc)

		self.modelMatrixLoc = glGetUniformLocation(self.renderingProgramID, "u_model_matrix")
		self.viewMatrixLoc = glGetUniformLocation(self.renderingProgramID, "u_view_matrix")
		self.projectionMatrixLoc = glGetUniformLocation(self.renderingProgramID, "u_projection_matrix")

		self.eyePosLoc = glGetUniformLocation(self.renderingProgramID, "u_eye_position")
		
		self.lightPosLoc = glGetUniformLocation(self.renderingProgramID, "u_light_position")
		self.lightDiffuseLoc = glGetUniformLocation(self.renderingProgramID, "u_light_diffuse")
		self.lightSpecularLoc = glGetUniformLocation(self.renderingProgramID, "u_light_specular")
		
		self.matDiffuseLoc = glGetUniformLocation(self.renderingProgramID, "u_mat_diffuse")
		self.matSpecularLoc = glGetUniformLocation(self.renderingProgramID, "u_mat_specular")
		self.matShininessLoc = glGetUniformLocation(self.renderingProgramID, "u_shininess")

		self.diffuseTextureLoc = glGetUniformLocation(self.renderingProgramID, "u_diffuse_tex")
		self.normalMapTextureLoc = glGetUniformLocation(self.renderingProgramID, "u_normal_map_tex")
		self.useDiffuseTextureLoc = glGetUniformLocation(self.renderingProgramID, "u_use_diffuse_tex")
		self.useNormalTextureLoc = glGetUniformLocation(self.renderingProgramID, "u_use_normal_tex")

		self.useFogLoc = glGetUniformLocation(self.renderingProgramID, "u_use_fog")
		self.fogMaxDistLoc = glGetUniformLocation(self.renderingProgramID, "u_fog_max_dist")
		self.fogMinDistLoc = glGetUniformLocation(self.renderingProgramID, "u_fog_min_dist")

		self.playerHealthLoc = glGetUniformLocation(self.renderingProgramID, "u_player_health")

	def use(self):
		try:
			glUseProgram(self.renderingProgramID)   
		except OpenGL.error.GLError:
			print(glGetProgramInfoLog(self.renderingProgramID))
			raise

	def set_model_matrix(self, matrix_array):
		glUniformMatrix4fv(self.modelMatrixLoc, 1, True, matrix_array)
	
	def set_view_matrix(self, matrix_array):
		glUniformMatrix4fv(self.viewMatrixLoc, 1, True, matrix_array)

	def set_projection_matrix(self, matrix_array):
		glUniformMatrix4fv(self.projectionMatrixLoc, 1, True, matrix_array)

	def set_eye_position(self, pos):
		glUniform4f(self.eyePosLoc, pos.x, pos.y, pos.z, 1.0)

	def set_light_position(self, pos):
		glUniform4f(self.lightPosLoc, pos.x, pos.y, pos.z, 1.0)
	
	def set_light_diffuse(self, red, green, blue):
		glUniform4f(self.lightDiffuseLoc, red, green, blue, 1.0)

	def set_light_specular(self, red, green, blue):
		glUniform4f(self.lightSpecularLoc, red, green, blue, 1.0)
	
	def set_material_diffuse(self, red, green, blue):
		glUniform4f(self.matDiffuseLoc, red, green, blue, 1.0)
	
	def set_material_diffuse_color(self, color):
		glUniform4f(self.matDiffuseLoc, color.r, color.g, color.b, 1.0)

	def set_material_specular(self, red, green, blue):
		glUniform4f(self.matSpecularLoc, red, green, blue, 1.0)
		
	def set_material_specular_color(self, color):
		glUniform4f(self.matSpecularLoc, color.r, color.g, color.b, 1.0)
		
	def set_material_shininess(self, shininess):
		glUniform1f(self.matShininessLoc, shininess)
	
	def set_player_health(self, val):
		glUniform1f(self.playerHealthLoc, val)

	def set_position_attribute(self, vertex_array):
		glVertexAttribPointer(self.positionLoc, 3, GL_FLOAT, False, 0, vertex_array)

	def set_normal_attribute(self, vertex_array):
		glVertexAttribPointer(self.normalLoc, 3, GL_FLOAT, GL_TRUE, 0, vertex_array)
	
	def set_uv_attribute(self, vertex_array):
		glVertexAttribPointer(self.uvLoc, 2, GL_FLOAT, False, 0, vertex_array)
	
	def set_diffuse_texture(self, tex):
		self.set_use_diffuse_texture(True)
		glUniform1i(self.diffuseTextureLoc, tex)
	
	def set_normal_map_texture(self, tex):
		self.set_use_normal_texture(True)
		glUniform1i(self.normalMapTextureLoc, tex)

	def set_use_diffuse_texture(self, val):
		glUniform1i(self.useDiffuseTextureLoc, val)
	
	def set_use_normal_texture(self, val):
		glUniform1i(self.useNormalTextureLoc, val)
	
	def set_attribute_buffers(self, vertex_buffer_id):
		glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_id)
		glVertexAttribPointer(self.positionLoc, 3, GL_FLOAT, False, 6 * sizeof(GLfloat), OpenGL.GLU.ctypes.c_void_p(0))
		glVertexAttribPointer(self.normalLoc, 3, GL_FLOAT, False, 6 * sizeof(GLfloat), OpenGL.GLU.ctypes.c_void_p(3 * sizeof(GLfloat)))

	def set_fog_max_distance(self, distance):
		glUniform1f(self.fogMaxDistLoc, distance)
	
	def set_fog_min_distance(self, distance):
		glUniform1f(self.fogMinDistLoc, distance)
	
	def set_use_fog(self, fog):
		glUniform1i(self.useFogLoc, fog)