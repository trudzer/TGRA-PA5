#version 330 core
uniform bool u_use_diffuse_tex;
uniform bool u_use_normal_tex;
uniform sampler2D u_diffuse_tex;
uniform sampler2D u_normal_map_tex;

uniform vec4 u_light_diffuse;
uniform vec4 u_light_specular;

uniform vec4 u_mat_diffuse;
uniform vec4 u_mat_specular;

uniform float u_shininess;

uniform float u_player_health;

uniform bool u_use_fog;
uniform float u_fog_max_dist;
uniform float u_fog_min_dist;

varying vec4 v_normal;
varying vec4 v_s;
varying vec4 v_h;
varying vec2 v_uv;
varying vec4 v_position;

vec4 calculate_normal_texture()
{
	// Get the normal vector from the texture and multiply it with the given normal
	vec4 tex_normal = texture2D(u_normal_map_tex, v_uv);
	
	vec4 normal = normalize(v_normal * vec4(tex_normal.rgb, 0.0));

	// Transform normal to range [-1,1]
	normal = normal * 2.0 - 1.0;
	normal = normalize(normal);
	return normal;
}

void main(void)
{
	vec4 mat_diffuse = u_mat_diffuse;
	vec4 normal = v_normal;
	
	if (u_use_diffuse_tex)
		mat_diffuse = u_mat_diffuse * texture2D(u_diffuse_tex, v_uv);
	
	if (u_use_normal_tex)
		normal = calculate_normal_texture();
	
	float lambert = max(dot(normal, v_s), 0);
	float phong = max(dot(v_normal, v_h), 0);

	vec4 shaded_color = u_light_diffuse * mat_diffuse * lambert + u_light_specular * u_mat_specular * pow(phong, u_shininess) + vec4(0.03, 0.03, 0.03, 1.0);
	float player_health_factor = u_player_health / 100;
	shaded_color.r = mix(1.0, shaded_color.r, player_health_factor);

	if (u_use_fog)
	{
		vec4 fog_color = vec4(0.0, 0.0, 0.0, 1.0);
		float fog_dist = length(v_position.xyz);
		float fog_factor = (u_fog_max_dist - fog_dist) / (u_fog_max_dist - u_fog_min_dist);
		fog_factor = clamp(fog_factor, 0.0, 1.0);
		shaded_color = mix(fog_color, shaded_color, fog_factor);
	}

	gl_FragColor = shaded_color;
}