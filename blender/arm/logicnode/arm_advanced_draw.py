import bpy
import gpu
from bgl import *
from mathutils import Vector
from gpu_extras.batch import batch_for_shader
from gpu_extras.presets import *
from math import pi, cos, sin

def getDpiFactor():
    return getDpi() / 72

def getDpi():
    systemPreferences = bpy.context.preferences.system
    retinaFactor = getattr(systemPreferences, "pixel_size", 1)
    return systemPreferences.dpi * retinaFactor

def getNodeBottomCornerLocations(node):
    region = bpy.context.region
    dpiFactor = getDpiFactor()
    location = node.getViewLocation() * dpiFactor
    dimensions = node.dimensions
    x = location.x
    y = location.y - dimensions.y

    viewToRegion = region.view2d.view_to_region
    leftBottom = Vector(viewToRegion(x, y, clip = False))
    rightBottom = Vector(viewToRegion(x + dimensions.x, y, clip = False))
    return leftBottom, rightBottom

class BlendSpaceGUI:
    def __init__(self, node):
        self.boundary = RectangleWithGrid()
        self.points = Points([])
        self.node = node

    def calculateBoundaries(self):
        dpiFactor = getDpiFactor()
        location = self.node.getViewLocation() * dpiFactor
        dimensions = self.node.dimensions
        x1 = location.x
        x2 = x1 + dimensions.x
        y1 = location.y - dimensions.y
        y2 = y1 - (x2 - x1)

        self.boundary.resetPosition(x1, y1, x2, y2)

    def getHeight(self):
        return self.boundary.height
    
    def setPointSize(self):
        self.node.point_size = self.points.point_size
    
    def setGUIBounds(self):
        self.node.gui_bounds = [self.boundary.x1 + self.boundary.offsetInner, self.boundary.y1 - self.boundary.offsetInner, self.boundary.widthInner]

    def draw(self):
        self.calculateBoundaries()
        self.boundary.draw()
        self.points.calcPoints(self.node.my_coords, self.node.my_coords_enabled, self.boundary.x1 + self.boundary.offsetInner, self.boundary.y1 - self.boundary.offsetInner, self.boundary.widthInner)
        self.setGUIBounds()
        self.setPointSize()
        self.points.drawPointCirc()

class Rectangle:
    def __init__(self, x1 = 0, y1 = 0, x2 = 0, y2 = 0):
        self.resetPosition(x1, y1, x2, y2)

    @classmethod
    def fromRegionDimensions(cls, region):
        return cls(0, 0, region.width, region.height)

    def resetPosition(self, x1 = 0, y1 = 0, x2 = 0, y2 = 0):
        self.x1 = float(x1)
        self.y1 =  float(y1)
        self.x2 =  float(x2)
        self.y2 =  float(y2)

    def copy(self):
        return Rectangle(self.x1, self.y1, self.x2, self.y2)

    @property
    def width(self):
        return abs(self.x1 - self.x2)

    @property
    def height(self):
        return abs(self.y1 - self.y2)

    @property
    def left(self):
        return min(self.x1, self.x2)

    @property
    def right(self):
        return max(self.x1, self.x2)

    @property
    def top(self):
        return max(self.y1, self.y2)

    @property
    def bottom(self):
        return min(self.y1, self.y2)

    @property
    def center(self):
        return Vector((self.centerX, self.centerY))

    @property
    def centerX(self):
        return (self.x1 + self.x2) / 2

    @property
    def centerY(self):
        return (self.y1 + self.y2) / 2

    def getInsetRectangle(self, amount):
        return Rectangle(self.left + amount, self.top - amount, self.right - amount, self.bottom + amount)

    def contains(self, point):
        return self.left <= point[0] <= self.right and self.bottom <= point[1] <= self.top

    def draw(self, color = (0.8, 0.8, 0.8, 1.0), borderColor = (0.1, 0.1, 0.1, 1.0), borderThickness = 0):
        locations = (
            (self.x1, self.y1),
            (self.x2, self.y1),
            (self.x1, self.y2),
            (self.x2, self.y2))
        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRI_STRIP', {"pos": locations})

        shader.bind()
        shader.uniform_float("color", color)

        glEnable(GL_BLEND)
        batch.draw(shader)
        glDisable(GL_BLEND)
        

        if borderThickness == 0: return

        offset = borderThickness // 2
        bWidth = offset * 2 if borderThickness > 0 else 0
        borderLocations = (
            (self.x1 - bWidth, self.y1 + offset), (self.x2 + bWidth, self.y1 + offset),
            (self.x2 + offset, self.y1 + bWidth), (self.x2 + offset, self.y2 - bWidth),
            (self.x2 + bWidth, self.y2 - offset), (self.x1 - bWidth, self.y2 - offset),
            (self.x1 - offset, self.y2 - bWidth), (self.x1 - offset, self.y1 + bWidth))
        batch = batch_for_shader(shader, 'LINES',{"pos": borderLocations})

        shader.bind()
        shader.uniform_float("color", borderColor)

        glEnable(GL_BLEND)
        glLineWidth(abs(borderThickness))
        batch.draw(shader)
        glDisable(GL_BLEND)

    def __repr__(self):
        return "({}, {}) - ({}, {})".format(self.x1, self.y1, self.x2, self.y2)

class Points:

    def __init__(self, points = []):
        self.points = points
        self.point_size = 0.025
        self.width = 0.0
        self.colors = [ (0.4, 0.5, 0.9, 0.4),
                        (1.0, 0.0, 1.0, 0.4),
                        (0.0, 1.0, 1.0, 0.4),
                        (1.0, 1.0, 0.0, 0.4),
                        (0.0, 0.0, 1.0, 0.4),
                        (0.0, 1.0, 0.0, 0.4),
                        (1.0, 0.0, 0.0, 0.4),
                        (0.8, 0.6, 1.0, 0.4),
                        (0.6, 0.8, 1.0, 0.4),
                        (1.0, 0.6, 0.8, 0.4), 
                        (1.0, 1.0, 1.0, 1.0)]
        self.circle_coords = self.circle(0.0, 0.0, self.point_size, 4)
        self.square_coord = self.circle(0.0, 0.0, self.point_size, 5)
        self.visible = []
    
    def get_points_list(self):
        p = []
        for p1 in self.points:
            for p2 in p1:
                p.append(p2)
        
        return p

    def calcPoints(self, points, visible, x1, y1, width):
        self.width = width
        self.points = []
        self.visible = visible

        for i in range(len(points) // 2):
            point = []
            point.append(x1 + width * points[i * 2])
            point.append(y1 - width + width * points[i * 2 + 1])
            self.points.append(point)

    def reset_circle(self, point):
        new_coords = []
        for coord in self.circle_coords:
            x = coord[0] * self.width + point[0]
            y = coord[1] * self.width + point[1]
            new_coords.append((x, y))
        return new_coords
    
    def reset_square(self, point):
        new_coords = []
        for coord in self.square_coord:
            x = coord[0] * self.width + point[0]
            y = coord[1] * self.width + point[1]
            new_coords.append((x, y))
        return new_coords
    
    def circle(self, x, y, radius, segments):
        coords = []
        m = (1.0 / (segments - 1)) * (pi * 2)

        for p in range(segments):
            p1 = x + cos(m * p) * radius
            p2 = y + sin(m * p) * radius
            coords.append((p1, p2))
        return coords
    
    def drawPointCirc(self):
        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        for i in range(len(self.points) - 1):
            if(self.visible[i]):
                circle_co = self.reset_circle(self.points[i])
                batch = batch_for_shader(shader, 'TRI_FAN',{"pos": circle_co})
                shader.bind()
                shader.uniform_float("color", self.colors[i])
                batch.draw(shader)
        square_co = self.reset_square(self.points[len(self.points) - 1])
        batch = batch_for_shader(shader, 'TRI_FAN',{"pos": square_co})
        shader.bind()
        shader.uniform_float("color", self.colors[len(self.points) - 1])
        batch.draw(shader)
        

    
class RectangleWithGrid:
    def __init__(self, x1 = 0, y1 = 0, x2 = 0, y2 = 0):
        self.resetPosition(x1, y1, x2, y2)
        self.numGrids = 21

    @classmethod
    def fromRegionDimensions(cls, region):
        return cls(0, 0, region.width, region.height)

    def resetPosition(self, x1 = 0, y1 = 0, x2 = 0, y2 = 0):
        self.x1 = float(x1)
        self.y1 =  float(y1)
        self.x2 =  float(x2)
        self.y2 =  float(y2)

    def copy(self):
        return Rectangle(self.x1, self.y1, self.x2, self.y2)

    @property
    def width(self):
        return abs(self.x1 - self.x2)
    
    @property
    def widthInner(self):
        return abs(self.width - (2 * self.width/self.numGrids))

    @property
    def offsetInner(self):
        return abs(self.width/self.numGrids)


    @property
    def height(self):
        return abs(self.y1 - self.y2)

    @property
    def left(self):
        return min(self.x1, self.x2)

    @property
    def right(self):
        return max(self.x1, self.x2)

    @property
    def top(self):
        return max(self.y1, self.y2)

    @property
    def bottom(self):
        return min(self.y1, self.y2)

    @property
    def center(self):
        return Vector((self.centerX, self.centerY))

    @property
    def centerX(self):
        return (self.x1 + self.x2) / 2

    @property
    def centerY(self):
        return (self.y1 + self.y2) / 2

    def getInsetRectangle(self, amount):
        return Rectangle(self.left + amount, self.top - amount, self.right - amount, self.bottom + amount)

    def contains(self, point):
        return self.left <= point[0] <= self.right and self.bottom <= point[1] <= self.top

    def draw(self, color = (0.5, 0.5, 0.5, 1.0), borderColor = (0.3, 0.3, 0.3, 1.0), gridColor = (0.5, 0.5, 0.5, 1.0), borderThickness = 3, gridLineThickness = 1):
        locations = (
            (self.x1, self.y1),
            (self.x2, self.y1),
            (self.x1, self.y2),
            (self.x2, self.y2))
        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRI_STRIP', {"pos": locations})

        shader.bind()
        shader.uniform_float("color", color)

        glEnable(GL_BLEND)
        batch.draw(shader)
        glDisable(GL_BLEND)

        locations = (
            (self.x1 + self.width/self.numGrids, self.y1 - self.height/self.numGrids),
            (self.x2 - self.width/self.numGrids, self.y1 - self.height/self.numGrids),
            (self.x1 + self.width/self.numGrids, self.y2 + self.height/self.numGrids),
            (self.x2 - self.width/self.numGrids, self.y2 + self.height/self.numGrids))
        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRI_STRIP', {"pos": locations})

        shader.bind()
        shader.uniform_float("color", borderColor)

        glEnable(GL_BLEND)
        batch.draw(shader)
        glDisable(GL_BLEND)

        if borderThickness == 0: return

        offset = borderThickness // 2
        borderLocations = (
            (self.x1, self.y1), (self.x2, self.y1),
            (self.x2, self.y1), (self.x2, self.y2),
            (self.x2, self.y2), (self.x1, self.y2),
            (self.x1, self.y2), (self.x1, self.y1),
            (self.centerX, self.y1), (self.centerX, self.y2),
            (self.x1, self.centerY), (self.x2, self.centerY))
        batch = batch_for_shader(shader, 'LINES',{"pos": borderLocations})

        shader.bind()
        shader.uniform_float("color", gridColor)

        glEnable(GL_BLEND)
        glLineWidth(abs(borderThickness))
        batch.draw(shader)
        glDisable(GL_BLEND)

        offset = (self.x2 - self.x1) / (self.numGrids + 1)
        gridPoints = []
        for l in range(21):
            p1 = (self.x1 + (offset * (l + 1)), self.y1)
            p2 = (self.x1 + (offset * (l + 1)), self.y2)
            gridPoints.append(p1)
            gridPoints.append(p2)
        for l in range(21):
            p1 = (self.x1, self.y1 - (offset * (l + 1)))
            p2 = (self.x2, self.y1 - (offset * (l + 1)))
            gridPoints.append(p1)
            gridPoints.append(p2)
        
        batch = batch_for_shader(shader, 'LINES',{"pos": gridPoints})

        shader.bind()
        shader.uniform_float("color", gridColor)
        
        glEnable(GL_BLEND)
        glLineWidth(abs(gridLineThickness))
        batch.draw(shader)
        glDisable(GL_BLEND)

    def __repr__(self):
        return "({}, {}) - ({}, {})".format(self.x1, self.y1, self.x2, self.y2)