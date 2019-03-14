import math


def compute(r):
    return math.sin(r)

def calc(template_x, template_y, template_z, field1, field2, field3):
	return math.sqrt((template_x-field1)**2 + (template_y-field2)**2 + (template_z-field3)**2)
