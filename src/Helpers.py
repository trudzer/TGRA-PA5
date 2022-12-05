from Base3DObjects import Vector
from math import acos

def look_at(obj_a, obj_b, base_rotation=0):
	look_vec = obj_b - obj_a
	look_vec.normalize()

	look_dir = look_vec.dot(Vector(0, 0, 1))

	if obj_b.x > obj_a.x:
		return acos(-look_dir) - base_rotation
	else:
		return acos(look_dir) + base_rotation