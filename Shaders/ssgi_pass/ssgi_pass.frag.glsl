#version 450

#include "compiled.inc"
#include "std/math.glsl"
#include "std/gbuffer.glsl"

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0; // Normal
#ifdef _RTGI
uniform sampler2D gbuffer1; // Basecol
#endif
uniform mat4 P;
uniform mat4 tiV;

uniform vec2 cameraProj;

// const int ssgiStrength = 1.0;
// const int ssgiMaxSteps = 16;
// const int ssgiBinarySteps = 4;
// const float ssgiRayStep = 0.005;
const float angleMix = 0.5f;
#ifdef _SSGICone9
const float strength = 2.0 * (1.0 / ssgiStrength);
#else
const float strength = 2.0 * (1.0 / ssgiStrength) * 1.8;
#endif

in vec3 viewRay;
in vec2 texCoord;
out vec4 fragColor;

vec3 hitCoord;
vec2 coord;
float depth;
float occ = 0.0;
#ifdef _RTGI
vec3 col = vec3(0.0);
#endif
vec3 vpos;

vec2 getProjectedCoord(vec3 hitCoord) {
	vec4 projectedCoord = P * vec4(hitCoord, 1.0);
	projectedCoord.xy /= projectedCoord.w;
	projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
	#ifdef _InvY
	projectedCoord.y = 1.0 - projectedCoord.y;
	#endif
	return projectedCoord.xy;
}

float getDeltaDepth(vec3 hitCoord) {
	coord = getProjectedCoord(hitCoord);
	depth = texture(gbufferD, coord).r * 2.0 - 1.0;
	vec3 p = getPosView(viewRay, depth, cameraProj);
	return p.z - hitCoord.z;
}

// void binarySearch(vec3 dir) {	
// 	for (int i = 0; i < ssgiBinarySteps; i++) {
// 		dir *= 0.5;
// 		hitCoord -= dir;
// 		if (getDeltaDepth(hitCoord) < 0.0) hitCoord += dir;
// 	}
// }

void rayCast(vec3 dir) {
	hitCoord = vpos;
	dir *= ssgiRayStep;
	#ifdef _SSGICone9
	float dist = 1.0 / 9.0;
	#else
	float dist = 1.0 / 5.0;
	#endif
	for (int i = 0; i < ssgiMaxSteps; i++) {
		hitCoord += dir;
		float delta = getDeltaDepth(hitCoord);
		if (delta > 0.0 && delta < 0.2) {
			dist = distance(vpos, hitCoord);
			/* binarySearch(dir); */ break;
		}
	}
	occ += dist;
	#ifdef _RTGI
	col += texture(gbuffer1, coord).rgb * ((ssgiRayStep * ssgiMaxSteps) - dist);
	#endif
}

vec3 tangent(const vec3 n) {
	vec3 t1 = cross(n, vec3(0, 0, 1));
	vec3 t2 = cross(n, vec3(0, 1, 0));
	if (length(t1) > length(t2)) return normalize(t1);
	else return normalize(t2);
}

void main() {
	vec4 g0 = texture(gbuffer0, texCoord);
	float d = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	// if (d == 1.0) { fragColor.rgb = vec3(0.0); return; }

	vec2 enc = g0.rg;
	vec4 n;
	n.z = 1.0 - abs(enc.x) - abs(enc.y);
	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	n.xyz = normalize(n.xyz);
	n.w = 1.0;
	n = tiV * n;
	n.xyz = normalize(n.xyz);

	vpos = getPosView(viewRay, d, cameraProj);

	rayCast(n.xyz);
	vec3 o1 = normalize(tangent(n.xyz));
	vec3 o2 = normalize(cross(o1, n.xyz));
	vec3 c1 = 0.5f * (o1 + o2);
	vec3 c2 = 0.5f * (o1 - o2);
	rayCast(mix(n.xyz, o1, angleMix));
	rayCast(mix(n.xyz, o2, angleMix));
	rayCast(mix(n.xyz, -c1, angleMix));
	rayCast(mix(n.xyz, -c2, angleMix));

	#ifdef _SSGICone9
	rayCast(mix(n.xyz, -o1, angleMix));
	rayCast(mix(n.xyz, -o2, angleMix));
	rayCast(mix(n.xyz, c1, angleMix));
	rayCast(mix(n.xyz, c2, angleMix));
	#endif
	
	#ifdef _RTGI
	fragColor.rgb = vec3((occ + col * occ) * strength);
	#else
	fragColor.r = occ * strength;
	#endif
}
