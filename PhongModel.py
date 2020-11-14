import math
import struct
from Funciones import *
from FuncionesM import *
from collections import namedtuple

class RayTracer(object):
    
    def __init__(self, filename):
      self.scene = []
      self.width = 0
      self.height = 0
      self.xVP = 0
      self.yVP = 0
      self.wVP = 0
      self.hVP = 0
      self.glClear()
      self.light = None
      self.clear_color = color(236,235,234)
      self.framebuffer = []
      self.filename = filename
      
    def glClear(self):
      self.framebuffer = [[self.clear_color for x in range(self.width)] for y in range(self.height)]
      self.zbuffer = [[-float('inf') for x in range(self.width)] for y in range(self.height)]

    def glpoint(self, x, y):
      self.framebuffer[y][x] = self.clear_color

    def glCreateWindow(self, width, height):
      self.width = width
      self.height = height

    def glClearColor(self, red, blue, green):
      self.clear_color = color(red, blue, green)

    def glViewPort(self, x, y, wVP, heightVP):
        self.xVP = x
        self.yVP = y
        self.wVP = wVP
        self.hVP = hVP

    def glVertex(self, x, y):
        x_Ver = int(round(self.wVP/2)*(x+1))
        y_Ver = int(round(self.yVP/2)*(x+1))
        x_pnt = self.xVP + x_Ver
        y_pnt = self.yVP + y_Ver
        self.glpoint((x_pnt),(y_pnt))

    def glLine(self, x1, y1, x2, y2):
      dy = abs(y2 - y1)
      dx = abs(x2 - x1)
      steep = dy > dx

      if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
        dy = abs(y2 - y1)
        dx = abs(x2 - x1)

      if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

      offset = 0
      threshold = 1
      y = y1
      for x in range(x1, x2):
        if steep:
          self.glpoint(y, x)
        else:
          self.glpoint(x, y)

        offset += dy * 2

        if offset >= threshold:
          y += 1 if y1 < y2 else -1
          threshold += 2 * dx

    def writebmp(self):
        
      f = open(self.filename, 'bw')
      f.write(char('B'))
      f.write(char('M'))
      f.write(dword(14 + 40 + self.width * self.height * 3))
      f.write(dword(0))
      f.write(dword(14 + 40))

      f.write(dword(40))
      f.write(dword(self.width))
      f.write(dword(self.height))
      f.write(word(1))
      f.write(word(24))
      f.write(dword(0))
      f.write(dword(self.width * self.height * 3))
      f.write(dword(0))
      f.write(dword(0))
      f.write(dword(0))
      f.write(dword(0))

      for x in range(self.height):
        for y in range(self.width):
          f.write(self.framebuffer[x][y].toBytes())
      f.close()

    def glFinish(self):
      self.writebmp()

    def cast_ray(self, orig, direction):
      material, impact = self.scene_intersect(orig, direction)

      if material is None:
        return self.clear_color

      light_dir = norm(sub(self.light.position, impact.point))
      light_distance = length(sub(self.light.position, impact.point))


      offset_normal = mul(impact.normal, 1.1)

      if dot(light_dir, impact.normal) <0:
        shadow_origin = sub(impact.point, offset_normal)
      else:
        shadow_origin = sum(impact.point, offset_normal)


      shadow_material, shadow_intersect = self.scene_intersect(shadow_origin,light_dir)
      shadow_intensity = 0

      if shadow_intersect and length(sub(shadow_intersect.point, shadow_origin)) < light_distance:
        shadow_intensity = 0.9

      intensity = self.light.intensity * max(0, dot(light_dir, impact.normal))*(1 - shadow_intensity)

      reflection = reflect(light_dir, impact.normal)
      specular_intensity = self.light.intensity * (
              max(0, -dot(reflection, direction)) ** material.spec
      )

      diffuse = material.diffuse * intensity * material.albedo[0]
      specular = color(255, 255, 255) * specular_intensity * material.albedo[1]
      return diffuse + specular


    def scene_intersect(self, orig, dir):
      zbuffer = float('inf')
      material = None
      intersect = None

      for obj in self.scene:
        hit = obj.ray_intersect(orig, dir)
        if hit is not None:
          if hit.distance < zbuffer:
            zbuffer = hit.distance
            material = obj.material
            intersect = hit

      return material, intersect


    def render(self):
      fun = int(math.pi / 2)
      for y in range(self.height):
        for x in range(self.width):
          i = (2 * (x + 0.5) / self.width - 1) * math.tan(fun / 2) * self.width / self.height
          j = (2 * (y + 0.5) / self.height - 1) * math.tan(fun / 2)
          direction = norm(V3(i, j, -1))
          self.framebuffer[y][x] = self.cast_ray(V3(0, 0, 0), direction)


ivory = Material(diffuse=color(100, 100, 80), albedo=(0.6, 0.4), spec=50)
rouge = Material(diffuse=color(220, 0, 0), albedo=(0.8,  0.2), spec=100)
noir = Material(diffuse=color(0, 0, 0), albedo=(.9, 0.1), spec=10)
blanc = Material(diffuse=color(255, 255, 255), albedo=(0.6, 0.3), spec=10)
cafeleger = Material(diffuse=color(255, 128, 0), albedo=(0.8, 0.2), spec=10)
cafe = Material(diffuse=color(102, 51, 0), albedo=(0.8, 0.2), spec=10)

r = RayTracer('Osooos.bmp')
r.glCreateWindow(1000,600)
r.glClear()

r.light = Light(
  color=color(255,255,255),
  position = V3(0,0, 20),
  intensity = 1.85
)


r.scene = [
#Ours blanc
    #Cabeza
    Sphere(V3(-2.1, 1.6, -10), 1.2, blanc),
    Sphere(V3(-1.65, 0.9, -8), 0.5, blanc),
    Sphere(V3(-3.3, 2.6, -11), 0.7, blanc),
    Sphere(V3(-1.4, 2.6, -11), 0.7, blanc),
    Sphere(V3(-1.2, 1.5, -8), 0.12, noir),
    Sphere(V3(-2.1, 1.5, -8), 0.12, noir),
    Sphere(V3(-1.43, 0.85, -7), 0.12, noir),

    #Cuerpo
    Sphere(V3(-2.2, -0.8, -11), 1.7, blanc),
    Sphere(V3(-3.8, -0.1, -10), 0.75, blanc),
    Sphere(V3(-0.4, -0.1, -10), 0.75, blanc),
    Sphere(V3(-3.2, -2.2, -10), 0.75, blanc),
    Sphere(V3(-0.8, -2.2, -10), 0.75, blanc),

#Ours cafe
    #Cabeza
    Sphere(V3(3.1, 1.6, -10), 1.2, cafeleger),
    Sphere(V3(2.65, 1, -8), 0.4, cafe),
    Sphere(V3(2.3, 2.6, -11), 0.6, cafe),
    Sphere(V3(4.4, 2.6, -11), 0.6, cafe),
    Sphere(V3(3, 1.5, -8), 0.12, noir),
    Sphere(V3(2.2, 1.5, -8), 0.12, noir),
    Sphere(V3(2.35, 0.95, -7), 0.12, noir),

    #Cuerpo
    Sphere(V3(3.2, -0.8, -11), 1.7, rouge),
    Sphere(V3(1.6, -0.1, -10), 0.75, cafeleger),
    Sphere(V3(4.6, -0.1, -10), 0.75, cafeleger),
    Sphere(V3(1.7, -2.2, -10), 0.75, cafeleger),
    Sphere(V3(4.5, -2.2, -10), 0.75, cafeleger),
    
]
r.render()
r.glFinish()
