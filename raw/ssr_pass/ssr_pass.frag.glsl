#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;
uniform sampler2D gbufferD;
uniform sampler2D gbuffer0; // Normal
uniform sampler2D gbuffer1; // Color, roughness
uniform mat4 P;
uniform mat4 tiV;

const int maxSteps = 20;
const int numBinarySearchSteps = 5;

const float rayStep = 0.04;
const float minRayStep = 0.05;
const float searchDist = 4.4;
const float falloffExp = 3.0;

in vec3 viewRay;
in vec2 texCoord;

vec3 hitCoord;
float depth;

// float rand(vec2 co) { // Unreliable
//   return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
// }

vec4 getProjectedCoord(vec3 hitCoord) {
	vec4 projectedCoord = P * vec4(hitCoord, 1.0);
	projectedCoord.xy /= projectedCoord.w;
	projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
	return projectedCoord;
}

vec3 getPos(float depth) {	
	const float znear = 0.1;
	const float zfar = 1000.0;
	const float projectionA = zfar / (zfar - znear);
	const float projectionB = (-zfar * znear) / (zfar - znear);
	float linearDepth = projectionB / (projectionA - depth);
	return viewRay * linearDepth;
}

float getDeltaDepth(vec3 hitCoord) {	
	// depth = 1.0 - texture(gbuffer0, getProjectedCoord(hitCoord).xy).a;
	depth = texture(gbufferD, getProjectedCoord(hitCoord).xy).r * 2.0 - 1.0;
	vec3 viewPos = getPos(depth);
	return viewPos.z - hitCoord.z;
}

vec3 binarySearch(vec3 dir) {	
    // for (int i = 0; i < numBinarySearchSteps; i++) {
		dir *= 0.5;
        hitCoord -= dir;
        if (getDeltaDepth(hitCoord) < 0.0) hitCoord += dir;
		
        dir *= 0.5;
        hitCoord -= dir;
        if (getDeltaDepth(hitCoord) < 0.0) hitCoord += dir;
		
        dir *= 0.5;
        hitCoord -= dir;
        if (getDeltaDepth(hitCoord) < 0.0) hitCoord += dir;
		
        dir *= 0.5;
        hitCoord -= dir;
        if (getDeltaDepth(hitCoord) < 0.0) hitCoord += dir;
		
        dir *= 0.5;
        hitCoord -= dir;
        if (getDeltaDepth(hitCoord) < 0.0) hitCoord += dir;
    // }
    return vec3(getProjectedCoord(hitCoord).xy, 0.0);
}

vec4 rayCast(vec3 dir) {
	dir *= rayStep;
	
    // for (int i = 0; i < maxSteps; i++) {
        hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		hitCoord += dir;
        if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		
		// hitCoord += dir;
        // if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		// hitCoord += dir;
        // if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		// hitCoord += dir;
        // if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		// hitCoord += dir;
        // if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		// hitCoord += dir;
        // if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		// hitCoord += dir;
        // if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		// hitCoord += dir;
        // if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		// hitCoord += dir;
        // if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		// hitCoord += dir;
        // if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
		// hitCoord += dir;
        // if (getDeltaDepth(hitCoord) > 0.0) return vec4(binarySearch(dir), 1.0);
    // }
    return vec4(0.0, 0.0, 0.0, 0.0);
}

vec2 octahedronWrap(vec2 v) {
    return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}

vec2 unpackFloat(float f) {
	float index = floor(f) / 1000.0;
	float alpha = fract(f);
	return vec2(index, alpha);
}

void main() {
    float roughness = unpackFloat(texture(gbuffer1, texCoord).a).x;
	float reflectivity = 1.0 - roughness;
    if (reflectivity == 0.0) discard;
	
	vec4 g0 = texture(gbuffer0, texCoord);
	vec2 enc = g0.rg;
    vec3 n;
    n.z = 1.0 - abs(enc.x) - abs(enc.y);
    n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
    n = normalize(n);
	
	vec4 viewNormal = vec4(n, 1.0);
	if (viewNormal.z <= 0.9) discard; // Only up facing surfaces for now
	viewNormal = tiV * normalize(viewNormal);
	
	// float d = 1.0 - g0.a;
	float d = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	vec3 viewPos = getPos(d);
	
	vec3 reflected = normalize(reflect((viewPos.xyz), normalize(viewNormal.xyz)));
	hitCoord = viewPos.xyz;
	
	vec3 dir = reflected * max(minRayStep, -viewPos.z);// * (1.0 - rand(texCoord) * 0.5);
	vec4 coords = rayCast(dir);

	vec2 deltaCoords = abs(vec2(0.5, 0.5) - coords.xy);
	float screenEdgeFactor = clamp(1.0 - (deltaCoords.x + deltaCoords.y), 0.0, 1.0);

	float intensity = pow(reflectivity, falloffExp) *
		screenEdgeFactor * clamp(-reflected.z, 0.0, 1.0) *
		clamp((searchDist - length(viewPos.xyz - hitCoord)) * (1.0 / searchDist), 0.0, 1.0) * coords.w;

	vec4 texColor = texture(tex, texCoord);
	vec4 reflCol = vec4(texture(tex, coords.xy).rgb, 1.0);
	gl_FragColor = texColor * (1.0 - intensity) + reflCol * intensity;
}
