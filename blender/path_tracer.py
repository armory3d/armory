# Based on WebGL Path Tracing by Evan Wallace 
# (http://madebyevan.com/webgl-path-tracing/)

import bpy
import os


bounces = '5'
epsilon = '0.0001'
infinity = '10000.0'
lightSize = 0.1
lightVal = 0.5

objects = None
sampleCount = 0

MATERIAL_DIFFUSE = 0
MATERIAL_MIRROR = 1
MATERIAL_GLOSSY = 2
material = MATERIAL_MIRROR

YELLOW_BLUE_CORNELL_BOX = 0
RED_GREEN_CORNELL_BOX = 1
environment = YELLOW_BLUE_CORNELL_BOX


def concat(objects, func):
    text = ''
    for i in range(0, len(objects)):
        text += func(objects[i])
    return text


tracerFragmentSourceHeader = """
#version 450
#ifdef GL_ES
precision mediump float;
#endif
in vec3 initialRay;
in vec2 texCoord;
uniform vec3 eye;
//uniform float textureWeight;
uniform float timeSinceStart;
//uniform sampler2D stexture;
uniform float glossiness;
vec3 roomCubeMin = vec3(-1.0, -1.0, -1.0);
vec3 roomCubeMax = vec3(1.0, 1.0, 1.0);
"""


# compute the near and far intersections of the cube (stored in the x and y components) using the slab method
# no intersection means vec.x > vec.y (really tNear > tFar)
intersectCubeSource = """
vec2 intersectCube(vec3 origin, vec3 ray, vec3 cubeMin, vec3 cubeMax) {
    vec3 tMin = (cubeMin - origin) / ray;
    vec3 tMax = (cubeMax - origin) / ray;
    vec3 t1 = min(tMin, tMax);
    vec3 t2 = max(tMin, tMax);
    float tNear = max(max(t1.x, t1.y), t1.z);
    float tFar = min(min(t2.x, t2.y), t2.z);
    return vec2(tNear, tFar);
}
"""


# given that hit is a point on the cube, what is the surface normal?
# TODO: do this with fewer branches
normalForCubeSource = """
vec3 normalForCube(vec3 hit, vec3 cubeMin, vec3 cubeMax) {
    if (hit.x < cubeMin.x + """ + epsilon + """) return vec3(-1.0, 0.0, 0.0);
    else if (hit.x > cubeMax.x - """ + epsilon + """) return vec3(1.0, 0.0, 0.0);
    else if (hit.y < cubeMin.y + """ + epsilon + """) return vec3(0.0, -1.0, 0.0);
    else if (hit.y > cubeMax.y - """ + epsilon + """) return vec3(0.0, 1.0, 0.0);
    else if (hit.z < cubeMin.z + """ + epsilon + """) return vec3(0.0, 0.0, -1.0);
    //else return vec3(0.0, 0.0, 1.0);
	return vec3(0.0, 0.0, 1.0);
}
"""


# compute the near intersection of a sphere
# no intersection returns a value of +infinity
intersectSphereSource = """
float intersectSphere(vec3 origin, vec3 ray, vec3 sphereCenter, float sphereRadius) {
    vec3 toSphere = origin - sphereCenter;
    float a = dot(ray, ray);
    float b = 2.0 * dot(toSphere, ray);
    float c = dot(toSphere, toSphere) - sphereRadius*sphereRadius;
    float discriminant = b*b - 4.0*a*c;
    if (discriminant > 0.0) {
        float t = (-b - sqrt(discriminant)) / (2.0 * a);
        if (t > 0.0) return t;
    }
    return """ + infinity + """;
}
"""


# given that hit is a point on the sphere, what is the surface normal?
normalForSphereSource = """
vec3 normalForSphere(vec3 hit, vec3 sphereCenter, float sphereRadius) {
    return (hit - sphereCenter) / sphereRadius;
}
"""


# random cosine-weighted distributed vector
# from http://www.rorydriscoll.com/2009/01/07/better-sampling/
cosineWeightedDirectionSource = """
vec3 cosineWeightedDirection(float seed, vec3 normal) {
    float u = random(vec3(12.9898, 78.233, 151.7182), seed);
    float v = random(vec3(63.7264, 10.873, 623.6736), seed);
    float r = sqrt(u);
    float angle = 6.283185307179586 * v;
    // compute basis from normal
    vec3 sdir, tdir;
    if (abs(normal.x) < 0.5) {
        sdir = cross(normal, vec3(1.0, 0.0, 0.0));
    }
	else {
        sdir = cross(normal, vec3(0.0, 1.0, 0.0));
    }
    tdir = cross(normal, sdir);
    return r*cos(angle)*sdir + r*sin(angle)*tdir + sqrt(1.0-u)*normal;
}
"""


# use the fragment position for randomness
randomSource = """
float random(vec3 scale, float seed) {
    return fract(sin(dot(texCoord.xyx + seed, scale)) * 43758.5453 + seed);
    // return fract(sin(dot(gl_FragCoord.xyz + seed, scale)) * 43758.5453 + seed);
}
"""


# random normalized vector
uniformlyRandomDirectionSource = """
vec3 uniformlyRandomDirection(float seed) {
    float u = random(vec3(12.9898, 78.233, 151.7182), seed);
    float v = random(vec3(63.7264, 10.873, 623.6736), seed);
    float z = 1.0 - 2.0 * u;
    float r = sqrt(1.0 - z * z);
    float angle = 6.283185307179586 * v;
    return vec3(r * cos(angle), r * sin(angle), z);
}
"""


# random vector in the unit sphere
# note: this is probably not statistically uniform, saw raising to 1/3 power somewhere but that looks wrong?
uniformlyRandomVectorSource = """
vec3 uniformlyRandomVector(float seed) {
    return uniformlyRandomDirection(seed) * sqrt(random(vec3(36.7539, 50.3658, 306.2759), seed));
}
"""


# compute specular lighting contribution
specularReflection = """
 vec3 reflectedLight = normalize(reflect(light - hit, normal));
 specularHighlight = max(0.0, dot(reflectedLight, normalize(hit - origin)));"""


# update ray using normal and bounce according to a diffuse reflection
newDiffuseRay = """
 ray = cosineWeightedDirection(time + float(bounce), normal);"""


# update ray using normal according to a specular reflection
newReflectiveRay = """
 ray = reflect(ray, normal);
 """ + specularReflection + """
 specularHighlight = 2.0 * pow(specularHighlight, 20.0);"""


# update ray using normal and bounce according to a glossy reflection
newGlossyRay = """
 ray = normalize(reflect(ray, normal)) + uniformlyRandomVector(time + float(bounce)) * glossiness;
 """ + specularReflection + """
 specularHighlight = pow(specularHighlight, 3.0);"""


yellowBlueCornellBox = """
 if (hit.x < -0.9999) surfaceColor = vec3(0.1, 0.5, 1.0); // blue 
 else if (hit.x > 0.9999) surfaceColor = vec3(1.0, 0.9, 0.1); // yellow"""


redGreenCornellBox = """
 if (hit.x < -0.9999) surfaceColor = vec3(1.0, 0.3, 0.1); // red
 else if (hit.x > 0.9999) surfaceColor = vec3(0.3, 1.0, 0.1); // green"""


def _getShadowTestCode(o):
    return o.getShadowTestCode()


def makeShadow(objects):
    return """
float shadow(vec3 origin, vec3 ray) {
    """ + concat(objects, _getShadowTestCode) + """
    return 1.0;
}"""


def _getIntersectCode(o):
    return o.getIntersectCode()


def _getMinimumIntersectCode(o):
    return o.getMinimumIntersectCode()
    

def _getNormalCalculationCode(o):
    return o.getNormalCalculationCode()


def makeCalculateColor(objects):
  return """
vec3 calculateColor(float time, vec3 origin, vec3 ray, vec3 light) {
    vec3 colorMask = vec3(1.0);
    vec3 accumulatedColor = vec3(0.0);
  
    // main raytracing loop
    for (int bounce = 0; bounce < """ + bounces + """; bounce++) {
      // compute the intersection with everything
      vec2 tRoom = intersectCube(origin, ray, roomCubeMin, roomCubeMax);
      """ + concat(objects, _getIntersectCode) + """

      // find the closest intersection
      float t = """ + infinity + """;
      if (tRoom.x < tRoom.y) t = tRoom.y;
      """ + concat(objects, _getMinimumIntersectCode) + """

      // info about hit
      vec3 hit = origin + ray * t;
      vec3 surfaceColor = vec3(0.75);
      float specularHighlight = 0.0;
      vec3 normal;

      // calculate the normal (and change wall color)
      if (t == tRoom.y) {
        normal = -normalForCube(hit, roomCubeMin, roomCubeMax);
        """ + [yellowBlueCornellBox, redGreenCornellBox][environment] + """
        """ + newDiffuseRay + """
      }
      else if (t == """ + infinity + """) {
        break;
      }
      else {
		int aa = 0;
        if (aa == 1) {aa = 0;} // hack to discard the first 'else' in 'else if'
        """ + concat(objects, _getNormalCalculationCode) + """
        """ + [newDiffuseRay, newReflectiveRay, newGlossyRay][material] + """
      }

      // compute diffuse lighting contribution
      vec3 toLight = light - hit;
      float diffuse = max(0.0, dot(normalize(toLight), normal));

      // trace a shadow ray to the light
      float shadowIntensity = shadow(hit + normal * """ + epsilon + """, toLight);

      // do light bounce
      colorMask *= surfaceColor;
      accumulatedColor += colorMask * (""" + str(lightVal) + """ * diffuse * shadowIntensity);
      accumulatedColor += colorMask * specularHighlight * shadowIntensity;

      // calculate next origin
      origin = hit;
    }

    return accumulatedColor;
  }
"""


def makeMain():
  return """
void main() {
  float time = timeSinceStart;
  vec3 col = vec3(0.0);
  const int samples = 1;
  
  for (int i = 0; i < samples; i++) {
	vec3 newLight = light + uniformlyRandomVector(time - 53.0) * """ + str(lightSize) + """;  
	col += calculateColor(time, eye, initialRay, newLight);
	time += 0.35;
  }
  
  gl_FragColor = vec4(vec3(col / samples), 1.0);
}
"""


def _getGlobalCode(o):
    return o.getGlobalCode()


def makeTracerFragmentSource(objects):
    return tracerFragmentSourceHeader + \
    concat(objects, _getGlobalCode) + \
    intersectCubeSource + \
    normalForCubeSource + \
    intersectSphereSource + \
    normalForSphereSource + \
    randomSource + \
    cosineWeightedDirectionSource + \
    uniformlyRandomDirectionSource + \
    uniformlyRandomVectorSource + \
    makeShadow(objects) + \
    makeCalculateColor(objects) + \
    makeMain()


class Sphere:
    def __init__(self, center, radius, id):
        self.center = center;
        self.radius = radius;
        self.centerStr = 'sphereCenter' + str(id);
        self.radiusStr = 'sphereRadius' + str(id);
        self.intersectStr = 'tSphere' + str(id);
        
    def getGlobalCode(self):
        return """
uniform vec3 """ + self.centerStr + """;
uniform float """ + self.radiusStr + """;"""
 
    def getIntersectCode(self):
        return """
 float """ + self.intersectStr + """ = intersectSphere(origin, ray, """ + self.centerStr + """, """ + self.radiusStr + """);""" 

    def getShadowTestCode(self):
        return """
 """ + self.getIntersectCode() + """
 if (""" + self.intersectStr + """ < 1.0) return 0.0;""" 

    def getMinimumIntersectCode(self):
        return """
 if (""" + self.intersectStr + """ < t) t = """ + self.intersectStr + """;"""

    def getNormalCalculationCode(self):
        return """
 else if (t == """ + self.intersectStr + """) normal = normalForSphere(hit, """ + self.centerStr + """, """ + self.radiusStr + """);"""     


class Cube:
    def __init__(self, minCorner, maxCorner, id):
        self.minCorner = minCorner;
        self.maxCorner = maxCorner;
        self.minStr = 'cubeMin' + str(id);
        self.maxStr = 'cubeMax' + str(id);
        self.intersectStr = 'tCube' + str(id);
        
    def getGlobalCode(self):
        return """
uniform vec3 """ + self.minStr + """;
uniform vec3 """ + self.maxStr + """;"""
 
    def getIntersectCode(self):
        return """
 vec2 """ + self.intersectStr + """ = intersectCube(origin, ray, """ + self.minStr + """, """ + self.maxStr + """);"""
 
    def getShadowTestCode(self):
        return """
 """ + self.getIntersectCode() + """ 
 if (""" + self.intersectStr + """.x > 0.0 && """ + self.intersectStr + """.x < 1.0 && """ + self.intersectStr + """.x < """ + self.intersectStr + """.y) return 0.0;"""
 
    def getMinimumIntersectCode(self):
        return """
 if (""" + self.intersectStr + """.x > 0.0 && """ + self.intersectStr + """.x < """ + self.intersectStr + """.y && """ + self.intersectStr + """.x < t) t = """ + self.intersectStr + """.x;"""

    def getNormalCalculationCode(self):
        return """
 // have to compare intersectStr.x < intersectStr.y otherwise two coplanar
 // cubes will look wrong (one cube will "steal" the hit from the other)
 else if (t == """ + self.intersectStr + """.x && """ + self.intersectStr + """.x < """ + self.intersectStr + """.y) normal = normalForCube(hit, """ + self.minStr + """, """ + self.maxStr + """);"""


class Light:
    def __init__(self):
        pass
        
    def getGlobalCode(self):
        return """uniform vec3 light;"""

    def getIntersectCode(self):
        return """"""

    def getShadowTestCode(self):
        return """"""

    def getMinimumIntersectCode(self):
        return """"""

    def getNormalCalculationCode(self):
        return """"""


def initObjects():
	nextObjectId = 0
	objects = []
	objects.append(Light())
	
	for o in bpy.context.scene.objects:
		if o.name.split('.', 1)[0] == 'Sphere':
			objects.append(Sphere([0, 0, 0], 0, nextObjectId))
			nextObjectId += 1
	
	return objects

objects = initObjects()


def compile(frag_path):
    with open(frag_path, 'w') as f:
        f.write(makeTracerFragmentSource(objects))
