
#version 450
#ifdef GL_ES
precision mediump float;
#endif
in vec3 initialRay;
in vec2 texCoord;
out vec4 fragColor;
uniform vec3 eye;
//uniform float textureWeight;
uniform float timeSinceStart;
//uniform sampler2D stexture;
uniform float glossiness;
//vec3 roomCubeMin = vec3(0.0, 0.0, 0.0);
//vec3 roomCubeMax = vec3(1.0, 1.0, 1.0);

vec3 origin;
vec3 ray;
vec3 colorMask = vec3(1.0);
vec3 accumulatedColor = vec3(0.0);
uniform vec3 light;
uniform vec3 cubeCenter0;
uniform vec3 cubeSize0;
uniform vec3 cubeColor0;
vec2 intersectCube(vec3 origin, vec3 ray, vec3 cubeCenter, vec3 cubeSize) {
    vec3 cubeMin = cubeCenter - cubeSize;
    vec3 cubeMax = cubeCenter + cubeSize;
    vec3 tMin = (cubeMin - origin) / ray;
    vec3 tMax = (cubeMax - origin) / ray;
    vec3 t1 = min(tMin, tMax);
    vec3 t2 = max(tMin, tMax);
    float tNear = max(max(t1.x, t1.y), t1.z);
    float tFar = min(min(t2.x, t2.y), t2.z);
    return vec2(tNear, tFar);
}

vec3 normalForCube(vec3 hit, vec3 cubeCenter, vec3 cubeSize) {
    vec3 cubeMin = cubeCenter - cubeSize;
    vec3 cubeMax = cubeCenter + cubeSize;
    if (hit.x < cubeMin.x + 0.0001) return vec3(-1.0, 0.0, 0.0);
    else if (hit.x > cubeMax.x - 0.0001) return vec3(1.0, 0.0, 0.0);
    else if (hit.y < cubeMin.y + 0.0001) return vec3(0.0, -1.0, 0.0);
    else if (hit.y > cubeMax.y - 0.0001) return vec3(0.0, 1.0, 0.0);
    else if (hit.z < cubeMin.z + 0.0001) return vec3(0.0, 0.0, -1.0);
    //else return vec3(0.0, 0.0, 1.0);
    return vec3(0.0, 0.0, 1.0);
}

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
    return 10000.0;
}

vec3 normalForSphere(vec3 hit, vec3 sphereCenter, float sphereRadius) {
    return (hit - sphereCenter) / sphereRadius;
}

float random(vec3 scale, float seed) {
    // return fract(sin(dot(texCoord.xyx + seed, scale)) * 43758.5453 + seed);
    float d = 43758.5453;
    float dt = dot(texCoord.xyx + seed,scale);
    float sn = mod(dt,3.1415926);
    return fract(sin(sn) * d);
}

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

vec3 uniformlyRandomDirection(float seed) {
    float u = random(vec3(12.9898, 78.233, 151.7182), seed);
    float v = random(vec3(63.7264, 10.873, 623.6736), seed);
    float z = 1.0 - 2.0 * u;
    float r = sqrt(1.0 - z * z);
    float angle = 6.283185307179586 * v;
    return vec3(r * cos(angle), r * sin(angle), z);
}

vec3 uniformlyRandomVector(float seed) {
    return uniformlyRandomDirection(seed) * sqrt(random(vec3(36.7539, 50.3658, 306.2759), seed));
}

float shadow(vec3 origin, vec3 ray) {
    
 
 vec2 tCube0 = intersectCube(origin, ray, cubeCenter0, cubeSize0); 
 if (tCube0.x > 0.0 && tCube0.x < 1.0 && tCube0.x < tCube0.y) return 0.0;
    return 1.0;
}
int doBounce(float time, vec3 light, int bounce) {
    // compute the intersection with everything
      
 vec2 tCube0 = intersectCube(origin, ray, cubeCenter0, cubeSize0);

      // find the closest intersection
      float t = 10000.0;
      
 if (tCube0.x > 0.0 && tCube0.x < tCube0.y && tCube0.x < t) t = tCube0.x;

      // info about hit
      vec3 hit = origin + ray * t;
      vec3 surfaceColor = vec3(0.75);
      float specularHighlight = 0.0;
      vec3 normal;

      if (t == 10000.0) {
        //break;
        return 0;
      }
      else {
        int aa = 0;
        if (aa == 1) {aa = 0;} // hack to discard the first 'else' in 'else if'
        
 // have to compare intersectStr.x < intersectStr.y otherwise two coplanar
 // cubes will look wrong (one cube will "steal" the hit from the other)
 else if (t == tCube0.x) { if (tCube0.x < tCube0.y) normal = normalForCube(hit, cubeCenter0, cubeSize0); surfaceColor = cubeColor0; }
        
 ray = cosineWeightedDirection(time + float(bounce), normal);
      }

      // compute diffuse lighting contribution
      vec3 toLight = light - hit;
      //float diffuse = max(0.0, dot(normalize(toLight), normal));
      float diffuse = max(0.0, dot(normalize(toLight), normal)) / dot(toLight,toLight);

      // do light bounce
      colorMask *= surfaceColor;
      //if (bounce > 0) {
        // trace a shadow ray to the light
        float shadowIntensity = shadow(hit + normal * 0.0001, toLight);
          
        accumulatedColor += colorMask * (0.5 * diffuse * shadowIntensity);
        accumulatedColor += colorMask * specularHighlight * shadowIntensity;
      //}

      // calculate next origin
      origin = hit;
      
    return 0;
}

vec3 calculateColor(float time, vec3 _origin, vec3 _ray, vec3 light) {
    //vec3 colorMask = vec3(1.0);
    //vec3 accumulatedColor = vec3(0.0);
  
    origin = _origin;
    ray = _ray;
  
    // main raytracing loop
    //for (int bounce = 0; bounce < 2; bounce++) {
        int a;
        a = doBounce(time, light, 0);
        a = doBounce(time, light, 1);
        a = doBounce(time, light, 2);
    //}

    return accumulatedColor;
  }

void main() {
  float time = 0.0;//timeSinceStart;
  //timeSinceStart % 46735.275 ) / 1000;
  vec3 col = vec3(0.0);
  const int samples = 1;
  vec3 newLight;
  
  //for (int i = 0; i < samples; i++) {  
    newLight = light + uniformlyRandomVector(time - 53.0) * 0.1;
col += calculateColor(time, eye, initialRay, newLight);
time += 0.35;

  //}
  
  fragColor = vec4(vec3(col / samples), 1.0);
  fragColor.rgb = pow(fragColor.rgb * 0.7, vec3(1.0 / 2.2));
}
