import math


def compute(r):
    return math.sin(r)

def calc(mean_x, mean_y, mean_z, field1, field2, field3):
	return math.sqrt((mean_x-field1)**2 + (mean_y-field2)**2 + (mean_z-field3)**2)
