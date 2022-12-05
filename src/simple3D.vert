#version 330 core
attribute vec3 a_position;
attribute vec3 a_normal;
attribute vec2 a_uv;

uniform mat4 u_model_matrix;
uniform mat4 u_view_matrix;
uniform mat4 u_projection_matrix;

uniform vec4 u_eye_position;
uniform vec4 u_light_position;

varying vec4 v_normal;
varying vec4 v_s;
varying vec4 v_h;
varying vec2 v_uv;
varying vec4 v_frag_pos;
varying vec4 v_cam_pos;
varying vec4 v_position;

void main(void)
{
	// Send the UV coordinates to the fragment shader
	v_uv = a_uv;
	v_cam_pos = u_eye_position;

	vec4 position = vec4(a_position.xyz, 1.0);
	vec4 normal = vec4(a_normal.xyz, 0.0);

	position = u_model_matrix * position;
	v_normal = normalize(u_model_matrix * normal);
	
	v_s = normalize(u_light_position - position);
	v_frag_pos = position;

	vec4 v = normalize(u_eye_position - position);
	v_h = normalize(v_s + v);
	
	position = u_projection_matrix * (u_view_matrix * position);
	v_position = position;
	gl_Position = position;
}