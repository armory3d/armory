
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
uniform vec3 light;
uniform vec3 sphereCenter0;
uniform float sphereRadius0;
uniform vec3 sphereCenter1;
uniform float sphereRadius1;
uniform vec3 sphereCenter2;
uniform float sphereRadius2;
uniform vec3 sphereCenter3;
uniform float sphereRadius3;
uniform vec3 sphereCenter4;
uniform float sphereRadius4;
uniform vec3 sphereCenter5;
uniform float sphereRadius5;
uniform vec3 sphereCenter6;
uniform float sphereRadius6;
uniform vec3 sphereCenter7;
uniform float sphereRadius7;
uniform vec3 sphereCenter8;
uniform float sphereRadius8;
uniform vec3 sphereCenter9;
uniform float sphereRadius9;
uniform vec3 sphereCenter10;
uniform float sphereRadius10;
uniform vec3 sphereCenter11;
uniform float sphereRadius11;
uniform vec3 sphereCenter12;
uniform float sphereRadius12;
uniform vec3 sphereCenter13;
uniform float sphereRadius13;
uniform vec3 sphereCenter14;
uniform float sphereRadius14;
uniform vec3 sphereCenter15;
uniform float sphereRadius15;
uniform vec3 sphereCenter16;
uniform float sphereRadius16;
uniform vec3 sphereCenter17;
uniform float sphereRadius17;
uniform vec3 sphereCenter18;
uniform float sphereRadius18;
uniform vec3 sphereCenter19;
uniform float sphereRadius19;
uniform vec3 sphereCenter20;
uniform float sphereRadius20;
uniform vec3 sphereCenter21;
uniform float sphereRadius21;
uniform vec3 sphereCenter22;
uniform float sphereRadius22;
uniform vec3 sphereCenter23;
uniform float sphereRadius23;
uniform vec3 sphereCenter24;
uniform float sphereRadius24;
uniform vec3 sphereCenter25;
uniform float sphereRadius25;
uniform vec3 sphereCenter26;
uniform float sphereRadius26;
uniform vec3 sphereCenter27;
uniform float sphereRadius27;
uniform vec3 sphereCenter28;
uniform float sphereRadius28;
uniform vec3 sphereCenter29;
uniform float sphereRadius29;
vec2 intersectCube(vec3 origin, vec3 ray, vec3 cubeMin, vec3 cubeMax) {
    vec3 tMin = (cubeMin - origin) / ray;
    vec3 tMax = (cubeMax - origin) / ray;
    vec3 t1 = min(tMin, tMax);
    vec3 t2 = max(tMin, tMax);
    float tNear = max(max(t1.x, t1.y), t1.z);
    float tFar = min(min(t2.x, t2.y), t2.z);
    return vec2(tNear, tFar);
}

vec3 normalForCube(vec3 hit, vec3 cubeMin, vec3 cubeMax) {
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
    return fract(sin(dot(texCoord.xyx + seed, scale)) * 43758.5453 + seed);
    // return fract(sin(dot(gl_FragCoord.xyz + seed, scale)) * 43758.5453 + seed);
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
 
 float tSphere11 = intersectSphere(origin, ray, sphereCenter11, sphereRadius11);
 if (tSphere11 < 1.0) return 0.0;
 
 float tSphere12 = intersectSphere(origin, ray, sphereCenter12, sphereRadius12);
 if (tSphere12 < 1.0) return 0.0;
 
 float tSphere13 = intersectSphere(origin, ray, sphereCenter13, sphereRadius13);
 if (tSphere13 < 1.0) return 0.0;
 
 float tSphere14 = intersectSphere(origin, ray, sphereCenter14, sphereRadius14);
 if (tSphere14 < 1.0) return 0.0;
 
 float tSphere15 = intersectSphere(origin, ray, sphereCenter15, sphereRadius15);
 if (tSphere15 < 1.0) return 0.0;
 
 float tSphere16 = intersectSphere(origin, ray, sphereCenter16, sphereRadius16);
 if (tSphere16 < 1.0) return 0.0;
 
 float tSphere17 = intersectSphere(origin, ray, sphereCenter17, sphereRadius17);
 if (tSphere17 < 1.0) return 0.0;
 
 float tSphere18 = intersectSphere(origin, ray, sphereCenter18, sphereRadius18);
 if (tSphere18 < 1.0) return 0.0;
 
 float tSphere19 = intersectSphere(origin, ray, sphereCenter19, sphereRadius19);
 if (tSphere19 < 1.0) return 0.0;
 
 float tSphere20 = intersectSphere(origin, ray, sphereCenter20, sphereRadius20);
 if (tSphere20 < 1.0) return 0.0;
 
 float tSphere21 = intersectSphere(origin, ray, sphereCenter21, sphereRadius21);
 if (tSphere21 < 1.0) return 0.0;
 
 float tSphere22 = intersectSphere(origin, ray, sphereCenter22, sphereRadius22);
 if (tSphere22 < 1.0) return 0.0;
 
 float tSphere23 = intersectSphere(origin, ray, sphereCenter23, sphereRadius23);
 if (tSphere23 < 1.0) return 0.0;
 
 float tSphere24 = intersectSphere(origin, ray, sphereCenter24, sphereRadius24);
 if (tSphere24 < 1.0) return 0.0;
 
 float tSphere25 = intersectSphere(origin, ray, sphereCenter25, sphereRadius25);
 if (tSphere25 < 1.0) return 0.0;
 
 float tSphere26 = intersectSphere(origin, ray, sphereCenter26, sphereRadius26);
 if (tSphere26 < 1.0) return 0.0;
 
 float tSphere27 = intersectSphere(origin, ray, sphereCenter27, sphereRadius27);
 if (tSphere27 < 1.0) return 0.0;
 
 float tSphere28 = intersectSphere(origin, ray, sphereCenter28, sphereRadius28);
 if (tSphere28 < 1.0) return 0.0;
 
 float tSphere29 = intersectSphere(origin, ray, sphereCenter29, sphereRadius29);
 if (tSphere29 < 1.0) return 0.0;
    return 1.0;
}
vec3 calculateColor(float time, vec3 origin, vec3 ray, vec3 light) {
    vec3 colorMask = vec3(1.0);
    vec3 accumulatedColor = vec3(0.0);
  
    // main raytracing loop
    for (int bounce = 0; bounce < 5; bounce++) {
      // compute the intersection with everything
      vec2 tRoom = intersectCube(origin, ray, roomCubeMin, roomCubeMax);
      
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
 float tSphere11 = intersectSphere(origin, ray, sphereCenter11, sphereRadius11);
 float tSphere12 = intersectSphere(origin, ray, sphereCenter12, sphereRadius12);
 float tSphere13 = intersectSphere(origin, ray, sphereCenter13, sphereRadius13);
 float tSphere14 = intersectSphere(origin, ray, sphereCenter14, sphereRadius14);
 float tSphere15 = intersectSphere(origin, ray, sphereCenter15, sphereRadius15);
 float tSphere16 = intersectSphere(origin, ray, sphereCenter16, sphereRadius16);
 float tSphere17 = intersectSphere(origin, ray, sphereCenter17, sphereRadius17);
 float tSphere18 = intersectSphere(origin, ray, sphereCenter18, sphereRadius18);
 float tSphere19 = intersectSphere(origin, ray, sphereCenter19, sphereRadius19);
 float tSphere20 = intersectSphere(origin, ray, sphereCenter20, sphereRadius20);
 float tSphere21 = intersectSphere(origin, ray, sphereCenter21, sphereRadius21);
 float tSphere22 = intersectSphere(origin, ray, sphereCenter22, sphereRadius22);
 float tSphere23 = intersectSphere(origin, ray, sphereCenter23, sphereRadius23);
 float tSphere24 = intersectSphere(origin, ray, sphereCenter24, sphereRadius24);
 float tSphere25 = intersectSphere(origin, ray, sphereCenter25, sphereRadius25);
 float tSphere26 = intersectSphere(origin, ray, sphereCenter26, sphereRadius26);
 float tSphere27 = intersectSphere(origin, ray, sphereCenter27, sphereRadius27);
 float tSphere28 = intersectSphere(origin, ray, sphereCenter28, sphereRadius28);
 float tSphere29 = intersectSphere(origin, ray, sphereCenter29, sphereRadius29);

      // find the closest intersection
      float t = 10000.0;
      if (tRoom.x < tRoom.y) t = tRoom.y;
      
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
 if (tSphere11 < t) t = tSphere11;
 if (tSphere12 < t) t = tSphere12;
 if (tSphere13 < t) t = tSphere13;
 if (tSphere14 < t) t = tSphere14;
 if (tSphere15 < t) t = tSphere15;
 if (tSphere16 < t) t = tSphere16;
 if (tSphere17 < t) t = tSphere17;
 if (tSphere18 < t) t = tSphere18;
 if (tSphere19 < t) t = tSphere19;
 if (tSphere20 < t) t = tSphere20;
 if (tSphere21 < t) t = tSphere21;
 if (tSphere22 < t) t = tSphere22;
 if (tSphere23 < t) t = tSphere23;
 if (tSphere24 < t) t = tSphere24;
 if (tSphere25 < t) t = tSphere25;
 if (tSphere26 < t) t = tSphere26;
 if (tSphere27 < t) t = tSphere27;
 if (tSphere28 < t) t = tSphere28;
 if (tSphere29 < t) t = tSphere29;

      // info about hit
      vec3 hit = origin + ray * t;
      vec3 surfaceColor = vec3(0.75);
      float specularHighlight = 0.0;
      vec3 normal;

      // calculate the normal (and change wall color)
      if (t == tRoom.y) {
        normal = -normalForCube(hit, roomCubeMin, roomCubeMax);
        
 if (hit.x < -0.9999) surfaceColor = vec3(0.1, 0.5, 1.0); // blue 
 else if (hit.x > 0.9999) surfaceColor = vec3(1.0, 0.9, 0.1); // yellow
        
 ray = cosineWeightedDirection(time + float(bounce), normal);
      }
      else if (t == 10000.0) {
        break;
      }
      else {
		int aa = 0;
        if (aa == 1) {aa = 0;} // hack to discard the first 'else' in 'else if'
        
 else if (t == tSphere0) normal = normalForSphere(hit, sphereCenter0, sphereRadius0);
 else if (t == tSphere1) normal = normalForSphere(hit, sphereCenter1, sphereRadius1);
 else if (t == tSphere2) normal = normalForSphere(hit, sphereCenter2, sphereRadius2);
 else if (t == tSphere3) normal = normalForSphere(hit, sphereCenter3, sphereRadius3);
 else if (t == tSphere4) normal = normalForSphere(hit, sphereCenter4, sphereRadius4);
 else if (t == tSphere5) normal = normalForSphere(hit, sphereCenter5, sphereRadius5);
 else if (t == tSphere6) normal = normalForSphere(hit, sphereCenter6, sphereRadius6);
 else if (t == tSphere7) normal = normalForSphere(hit, sphereCenter7, sphereRadius7);
 else if (t == tSphere8) normal = normalForSphere(hit, sphereCenter8, sphereRadius8);
 else if (t == tSphere9) normal = normalForSphere(hit, sphereCenter9, sphereRadius9);
 else if (t == tSphere10) normal = normalForSphere(hit, sphereCenter10, sphereRadius10);
 else if (t == tSphere11) normal = normalForSphere(hit, sphereCenter11, sphereRadius11);
 else if (t == tSphere12) normal = normalForSphere(hit, sphereCenter12, sphereRadius12);
 else if (t == tSphere13) normal = normalForSphere(hit, sphereCenter13, sphereRadius13);
 else if (t == tSphere14) normal = normalForSphere(hit, sphereCenter14, sphereRadius14);
 else if (t == tSphere15) normal = normalForSphere(hit, sphereCenter15, sphereRadius15);
 else if (t == tSphere16) normal = normalForSphere(hit, sphereCenter16, sphereRadius16);
 else if (t == tSphere17) normal = normalForSphere(hit, sphereCenter17, sphereRadius17);
 else if (t == tSphere18) normal = normalForSphere(hit, sphereCenter18, sphereRadius18);
 else if (t == tSphere19) normal = normalForSphere(hit, sphereCenter19, sphereRadius19);
 else if (t == tSphere20) normal = normalForSphere(hit, sphereCenter20, sphereRadius20);
 else if (t == tSphere21) normal = normalForSphere(hit, sphereCenter21, sphereRadius21);
 else if (t == tSphere22) normal = normalForSphere(hit, sphereCenter22, sphereRadius22);
 else if (t == tSphere23) normal = normalForSphere(hit, sphereCenter23, sphereRadius23);
 else if (t == tSphere24) normal = normalForSphere(hit, sphereCenter24, sphereRadius24);
 else if (t == tSphere25) normal = normalForSphere(hit, sphereCenter25, sphereRadius25);
 else if (t == tSphere26) normal = normalForSphere(hit, sphereCenter26, sphereRadius26);
 else if (t == tSphere27) normal = normalForSphere(hit, sphereCenter27, sphereRadius27);
 else if (t == tSphere28) normal = normalForSphere(hit, sphereCenter28, sphereRadius28);
 else if (t == tSphere29) normal = normalForSphere(hit, sphereCenter29, sphereRadius29);
        
 ray = reflect(ray, normal);
 
 vec3 reflectedLight = normalize(reflect(light - hit, normal));
 specularHighlight = max(0.0, dot(reflectedLight, normalize(hit - origin)));
 specularHighlight = 2.0 * pow(specularHighlight, 20.0);
      }

      // compute diffuse lighting contribution
      vec3 toLight = light - hit;
      float diffuse = max(0.0, dot(normalize(toLight), normal));

      // trace a shadow ray to the light
      float shadowIntensity = shadow(hit + normal * 0.0001, toLight);

      // do light bounce
      colorMask *= surfaceColor;
      accumulatedColor += colorMask * (0.8 * diffuse * shadowIntensity);
      accumulatedColor += colorMask * specularHighlight * shadowIntensity;

      // calculate next origin
      origin = hit;
    }

    return accumulatedColor;
  }

void main() {
  float time = timeSinceStart;
  vec3 col = vec3(0.0);
  const int samples = 1;
  
  for (int i = 0; i < samples; i++) {
	vec3 newLight = light + uniformlyRandomVector(time - 53.0) * 0.1;  
	col += calculateColor(time, eye, initialRay, newLight);
	time += 0.35;
  }
  
  gl_FragColor = vec4(vec3(col / samples), 1.0);
}
