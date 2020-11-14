import struct
import math
from collections import namedtuple
from FuncionesM import *

def char(c):
    return struct.pack('=c', c.encode('ascii'))

def word(c):
    return struct.pack('=h', c)

def dword(c):
    return struct.pack('=l', c)

class color(object):
  def __init__(self,r,g,b):
    self.r = r
    self.g = g
    self.b = b

  def __add__(self, other_color):
    r = self.r + other_color.r
    g = self.g + other_color.g
    b = self.b + other_color.b

    return color(r,g,b)

  def __mul__(self, other):
    r = self.r * other
    g = self.g * other
    b = self.b * other

    return color(r,g,b)
  __rmul__ = __mul__

  def __repr__(self):
    return "color(%s, %s, %s)" % (self.r, self.g,self.b)

  def toBytes(self):
    self.r = int(max(min(self.r, 255), 0))
    self.g = int(max(min(self.g, 255), 0))
    self.b = int(max(min(self.b, 255), 0))
    return bytes([self.b,self.g,self.r])

class Light(object):
  def __init__(self, color =color(255,255,255),position =V3(0,0,0), intensity = 1):
    self.color = color
    self.position = position
    self.intensity = intensity


class Material(object):
  def __init__(self, diffuse =color(255,255,255), albedo=(1,0), spec=0):
    self.diffuse = diffuse
    self.albedo = albedo
    self.spec = spec

class Intersect(object):
  def __init__(self, distance=0, point=None, normal= None):
    self.distance = distance
    self.point = point
    self.normal = normal

class Sphere(object):
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    def ray_intersect(self, orig, direction):
        L = sub(self.center, orig)
        tca = dot(L, direction)
        l = length(L)
        d2 = l**2 - tca**2

        if d2 > self.radius**2:
            return None

        thc = (self.radius**2 - d2) ** 0.5
        t0 = tca - thc
        t1 = tca + thc

        if t0 < 0:
            t0 = t1
        if t0 < 0:
            return None

        hit = sum(orig, mul(direction, t0))
        normal = norm(sub(hit, self.center))

        return Intersect(
            distance=t0,
            point=hit,
            normal=normal
        )
