
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
//vec3 roomCubeMin = vec3(0.0, 0.0, 0.0);
//vec3 roomCubeMax = vec3(1.0, 1.0, 1.0);

vec3 origin;
vec3 ray;
vec3 colorMask = vec3(1.0);
vec3 accumulatedColor = vec3(0.0);
uniform vec3 light;
uniform vec3 sphereCenter0;
uniform float sphereRadius0;
uniform vec3 sphereColor0;
uniform vec3 sphereCenter1;
uniform float sphereRadius1;
uniform vec3 sphereColor1;
uniform vec3 sphereCenter2;
uniform float sphereRadius2;
uniform vec3 sphereColor2;
uniform vec3 sphereCenter3;
uniform float sphereRadius3;
uniform vec3 sphereColor3;
uniform vec3 sphereCenter4;
uniform float sphereRadius4;
uniform vec3 sphereColor4;
uniform vec3 sphereCenter5;
uniform float sphereRadius5;
uniform vec3 sphereColor5;
uniform vec3 sphereCenter6;
uniform float sphereRadius6;
uniform vec3 sphereColor6;
uniform vec3 sphereCenter7;
uniform float sphereRadius7;
uniform vec3 sphereColor7;
uniform vec3 sphereCenter8;
uniform float sphereRadius8;
uniform vec3 sphereColor8;
uniform vec3 sphereCenter9;
uniform float sphereRadius9;
uniform vec3 sphereColor9;
uniform vec3 sphereCenter10;
uniform float sphereRadius10;
uniform vec3 sphereColor10;
uniform vec3 cubeCenter0;
uniform vec3 cubeSize0;
uniform vec3 cubeColor0;
uniform vec3 cubeCenter1;
uniform vec3 cubeSize1;
uniform vec3 cubeColor1;
uniform vec3 cubeCenter2;
uniform vec3 cubeSize2;
uniform vec3 cubeColor2;
uniform vec3 cubeCenter3;
uniform vec3 cubeSize3;
uniform vec3 cubeColor3;
uniform vec3 cubeCenter4;
uniform vec3 cubeSize4;
uniform vec3 cubeColor4;
uniform vec3 cubeCenter5;
uniform vec3 cubeSize5;
uniform vec3 cubeColor5;
uniform vec3 sphereCenter11;
uniform float sphereRadius11;
uniform vec3 sphereColor11;
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
    
 
 float tSphere0 = intersectSphere(origin, ray, sphereCenter0, sphereRadius0);
 if (tSphere0 < 1.0) return 0.0;
 
 float tSphere1 = intersectSphere(origin, ray, sphereCenter1, sphereRadius1);
 if (tSphere1 < 1.0) return 0.0;
 
 float tSphere2 = intersectSphere(origin, ray, sphereCenter2, sphereRadius2);
 if (tSphere2 < 1.0) return 0.0;
 
 float tSphere3 = intersectSphere(origin, ray, sphereCenter3, sphereRadius3);
 if (tSphere3 < 1.0) return 0.0;
 
 float tSphere4 = intersectSphere(origin, ray, sphereCenter4, sphereRadius4);
 if (tSphere4 < 1.0) return 0.0;
 
 float tSphere5 = intersectSphere(origin, ray, sphereCenter5, sphereRadius5);
 if (tSphere5 < 1.0) return 0.0;
 
 float tSphere6 = intersectSphere(origin, ray, sphereCenter6, sphereRadius6);
 if (tSphere6 < 1.0) return 0.0;
 
 float tSphere7 = intersectSphere(origin, ray, sphereCenter7, sphereRadius7);
 if (tSphere7 < 1.0) return 0.0;
 
 float tSphere8 = intersectSphere(origin, ray, sphereCenter8, sphereRadius8);
 if (tSphere8 < 1.0) return 0.0;
 
 float tSphere9 = intersectSphere(origin, ray, sphereCenter9, sphereRadius9);
 if (tSphere9 < 1.0) return 0.0;
 
 float tSphere10 = intersectSphere(origin, ray, sphereCenter10, sphereRadius10);
 if (tSphere10 < 1.0) return 0.0;
 
 vec2 tCube0 = intersectCube(origin, ray, cubeCenter0, cubeSize0); 
 if (tCube0.x > 0.0 && tCube0.x < 1.0 && tCube0.x < tCube0.y) return 0.0;
 
 vec2 tCube1 = intersectCube(origin, ray, cubeCenter1, cubeSize1); 
 if (tCube1.x > 0.0 && tCube1.x < 1.0 && tCube1.x < tCube1.y) return 0.0;
 
 vec2 tCube2 = intersectCube(origin, ray, cubeCenter2, cubeSize2); 
 if (tCube2.x > 0.0 && tCube2.x < 1.0 && tCube2.x < tCube2.y) return 0.0;
 
 vec2 tCube3 = intersectCube(origin, ray, cubeCenter3, cubeSize3); 
 if (tCube3.x > 0.0 && tCube3.x < 1.0 && tCube3.x < tCube3.y) return 0.0;
 
 vec2 tCube4 = intersectCube(origin, ray, cubeCenter4, cubeSize4); 
 if (tCube4.x > 0.0 && tCube4.x < 1.0 && tCube4.x < tCube4.y) return 0.0;
 
 vec2 tCube5 = intersectCube(origin, ray, cubeCenter5, cubeSize5); 
 if (tCube5.x > 0.0 && tCube5.x < 1.0 && tCube5.x < tCube5.y) return 0.0;
 
 float tSphere11 = intersectSphere(origin, ray, sphereCenter11, sphereRadius11);
 if (tSphere11 < 1.0) return 0.0;
    return 1.0;
}
int doBounce(float time, vec3 light, int bounce) {
    // compute the intersection with everything
      
 float tSphere0 = intersectSphere(origin, ray, sphereCenter0, sphereRadius0);
 float tSphere1 = intersectSphere(origin, ray, sphereCenter1, sphereRadius1);
 float tSphere2 = intersectSphere(origin, ray, sphereCenter2, sphereRadius2);
 float tSphere3 = intersectSphere(origin, ray, sphereCenter3, sphereRadius3);
 float tSphere4 = intersectSphere(origin, ray, sphereCenter4, sphereRadius4);
 float tSphere5 = intersectSphere(origin, ray, sphereCenter5, sphereRadius5);
 float tSphere6 = intersectSphere(origin, ray, sphereCenter6, sphereRadius6);
 float tSphere7 = intersectSphere(origin, ray, sphereCenter7, sphereRadius7);
 float tSphere8 = intersectSphere(origin, ray, sphereCenter8, sphereRadius8);
 float tSphere9 = intersectSphere(origin, ray, sphereCenter9, sphereRadius9);
 float tSphere10 = intersectSphere(origin, ray, sphereCenter10, sphereRadius10);
 vec2 tCube0 = intersectCube(origin, ray, cubeCenter0, cubeSize0);
 vec2 tCube1 = intersectCube(origin, ray, cubeCenter1, cubeSize1);
 vec2 tCube2 = intersectCube(origin, ray, cubeCenter2, cubeSize2);
 vec2 tCube3 = intersectCube(origin, ray, cubeCenter3, cubeSize3);
 vec2 tCube4 = intersectCube(origin, ray, cubeCenter4, cubeSize4);
 vec2 tCube5 = intersectCube(origin, ray, cubeCenter5, cubeSize5);
 float tSphere11 = intersectSphere(origin, ray, sphereCenter11, sphereRadius11);

      // find the closest intersection
      float t = 10000.0;
      
 if (tSphere0 < t) t = tSphere0;
 if (tSphere1 < t) t = tSphere1;
 if (tSphere2 < t) t = tSphere2;
 if (tSphere3 < t) t = tSphere3;
 if (tSphere4 < t) t = tSphere4;
 if (tSphere5 < t) t = tSphere5;
 if (tSphere6 < t) t = tSphere6;
 if (tSphere7 < t) t = tSphere7;
 if (tSphere8 < t) t = tSphere8;
 if (tSphere9 < t) t = tSphere9;
 if (tSphere10 < t) t = tSphere10;
 if (tCube0.x > 0.0 && tCube0.x < tCube0.y && tCube0.x < t) t = tCube0.x;
 if (tCube1.x > 0.0 && tCube1.x < tCube1.y && tCube1.x < t) t = tCube1.x;
 if (tCube2.x > 0.0 && tCube2.x < tCube2.y && tCube2.x < t) t = tCube2.x;
 if (tCube3.x > 0.0 && tCube3.x < tCube3.y && tCube3.x < t) t = tCube3.x;
 if (tCube4.x > 0.0 && tCube4.x < tCube4.y && tCube4.x < t) t = tCube4.x;
 if (tCube5.x > 0.0 && tCube5.x < tCube5.y && tCube5.x < t) t = tCube5.x;
 if (tSphere11 < t) t = tSphere11;

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
        
 else if (t == tSphere0) { normal = normalForSphere(hit, sphereCenter0, sphereRadius0); surfaceColor = sphereColor0; }
 else if (t == tSphere1) { normal = normalForSphere(hit, sphereCenter1, sphereRadius1); surfaceColor = sphereColor1; }
 else if (t == tSphere2) { normal = normalForSphere(hit, sphereCenter2, sphereRadius2); surfaceColor = sphereColor2; }
 else if (t == tSphere3) { normal = normalForSphere(hit, sphereCenter3, sphereRadius3); surfaceColor = sphereColor3; }
 else if (t == tSphere4) { normal = normalForSphere(hit, sphereCenter4, sphereRadius4); surfaceColor = sphereColor4; }
 else if (t == tSphere5) { normal = normalForSphere(hit, sphereCenter5, sphereRadius5); surfaceColor = sphereColor5; }
 else if (t == tSphere6) { normal = normalForSphere(hit, sphereCenter6, sphereRadius6); surfaceColor = sphereColor6; }
 else if (t == tSphere7) { normal = normalForSphere(hit, sphereCenter7, sphereRadius7); surfaceColor = sphereColor7; }
 else if (t == tSphere8) { normal = normalForSphere(hit, sphereCenter8, sphereRadius8); surfaceColor = sphereColor8; }
 else if (t == tSphere9) { normal = normalForSphere(hit, sphereCenter9, sphereRadius9); surfaceColor = sphereColor9; }
 else if (t == tSphere10) { normal = normalForSphere(hit, sphereCenter10, sphereRadius10); surfaceColor = sphereColor10; }
 // have to compare intersectStr.x < intersectStr.y otherwise two coplanar
 // cubes will look wrong (one cube will "steal" the hit from the other)
 else if (t == tCube0.x) { if (tCube0.x < tCube0.y) normal = normalForCube(hit, cubeCenter0, cubeSize0); surfaceColor = cubeColor0; }
 // have to compare intersectStr.x < intersectStr.y otherwise two coplanar
 // cubes will look wrong (one cube will "steal" the hit from the other)
 else if (t == tCube1.x) { if (tCube1.x < tCube1.y) normal = normalForCube(hit, cubeCenter1, cubeSize1); surfaceColor = cubeColor1; }
 // have to compare intersectStr.x < intersectStr.y otherwise two coplanar
 // cubes will look wrong (one cube will "steal" the hit from the other)
 else if (t == tCube2.x) { if (tCube2.x < tCube2.y) normal = normalForCube(hit, cubeCenter2, cubeSize2); surfaceColor = cubeColor2; }
 // have to compare intersectStr.x < intersectStr.y otherwise two coplanar
 // cubes will look wrong (one cube will "steal" the hit from the other)
 else if (t == tCube3.x) { if (tCube3.x < tCube3.y) normal = normalForCube(hit, cubeCenter3, cubeSize3); surfaceColor = cubeColor3; }
 // have to compare intersectStr.x < intersectStr.y otherwise two coplanar
 // cubes will look wrong (one cube will "steal" the hit from the other)
 else if (t == tCube4.x) { if (tCube4.x < tCube4.y) normal = normalForCube(hit, cubeCenter4, cubeSize4); surfaceColor = cubeColor4; }
 // have to compare intersectStr.x < intersectStr.y otherwise two coplanar
 // cubes will look wrong (one cube will "steal" the hit from the other)
 else if (t == tCube5.x) { if (tCube5.x < tCube5.y) normal = normalForCube(hit, cubeCenter5, cubeSize5); surfaceColor = cubeColor5; }
 else if (t == tSphere11) { normal = normalForSphere(hit, sphereCenter11, sphereRadius11); surfaceColor = sphereColor11; }
        
 ray = reflect(ray, normal);
 
 vec3 reflectedLight = normalize(reflect(light - hit, normal));
 specularHighlight = max(0.0, dot(reflectedLight, normalize(hit - origin)));
 specularHighlight = 2.0 * pow(specularHighlight, 20.0);
      }

      // compute diffuse lighting contribution
      vec3 toLight = light - hit;
      //float diffuse = max(0.0, dot(normalize(toLight), normal));
      float diffuse = max(0.0, dot(normalize(toLight), normal)) / dot(toLight,toLight);

      // do light bounce
      colorMask *= surfaceColor;
      //if (bounce > 0) {
        // trace a shadow ray to the light
        float shadowIntensity = 1.0;//shadow(hit + normal * 0.0001, toLight);
          
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
  
  gl_FragColor = vec4(vec3(col / samples), 1.0);
  gl_FragColor.rgb = pow(gl_FragColor.rgb * 0.7, vec3(1.0 / 2.2));
}
