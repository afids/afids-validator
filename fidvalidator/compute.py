import math


def compute(r):
    return math.sin(r)

def calc(template_x, template_y, template_z, user_x, user_y, user_z):
    return math.sqrt((template_x-user_x)**2 + (template_y-user_y)**2 + (template_z-user_z)**2)
