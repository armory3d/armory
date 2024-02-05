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
uniform mat3 V3;

uniform vec2 cameraProj;

const int ssgiMaxSteps = int(ceil(1.0 / ssgiRayStep) * ssgiSearchDist);

const float angleMix = 0.5f;
#ifdef _SSGICone9
const float strength = 2.0 * (1.0 / ssgiStrength);
#else
const float strength = 2.0 * (1.0 / ssgiStrength) * 1.8;
#endif

in vec3 viewRay;
in vec2 texCoord;
#ifdef _RTGI
out vec4 fragColor;
#else
out float fragColor;
#endif

vec3 hitCoord;
vec2 coord;
float depth;
#ifdef _RTGI
vec3 col = vec3(0.0);
#endif
vec3 vpos;

vec2 getProjectedCoord(vec3 hitCoord) {
	vec4 projectedCoord = P * vec4(hitCoord, 1.0);
	projectedCoord.xy /= projectedCoord.w;
	projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
	#ifdef HLSL
	projectedCoord.y = 1.0 - projectedCoord.y;
	#endif
	return projectedCoord.xy;
}

float getDeltaDepth(vec3 hitCoord) {
	coord = getProjectedCoord(hitCoord);
	depth = textureLod(gbufferD, coord, 0.0).r * 2.0 - 1.0;
	vec3 p = getPosView(viewRay, depth, cameraProj);
	return p.z - hitCoord.z;
}

float binarySearch(vec3 dir) {
	float ddepth;
	for (int i = 0; i < 7; i++) {
		dir *= 0.5;
		hitCoord -= dir;
		ddepth = getDeltaDepth(hitCoord);
		if (ddepth < 0.0) hitCoord += dir;
	}
	if (abs(ddepth) > ssgiSearchDist * ssgiRayStep) return 0.0;
	return distance(vpos, hitCoord);
}

void rayCast(vec3 dir) {
	hitCoord = vpos;
	dir *= ssgiRayStep;
	float dist = 1.0;
	for (int i = 0; i < ssgiMaxSteps; i++) {
		hitCoord += dir;
		float delta = getDeltaDepth(hitCoord);
		if (delta > 0.0 && delta < 1.0) {
			dist = binarySearch(dir);
			break;
		}
	}
	#ifdef _RTGI
	if (dist != 0 && dist != 1.0)
		col += textureLod(gbuffer1, coord, 0.0).rgb * ((ssgiRayStep * ssgiMaxSteps) - dist);
	#else
	fragColor.r += dist;
	#endif
}

vec3 tangent(const vec3 n) {
	vec3 t1 = cross(n, vec3(0, 0, 1));
	vec3 t2 = cross(n, vec3(0, 1, 0));
	if (length(t1) > length(t2)) return normalize(t1);
	else return normalize(t2);
}

void main() {
	#ifdef _RTGI
	fragColor = vec4(0.0);
	#else
	fragColor = 0.0;
	#endif
	vec4 g0 = textureLod(gbuffer0, texCoord, 0.0);
	float d = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;

	vec2 enc = g0.rg;
	vec3 n;
	n.z = 1.0 - abs(enc.x) - abs(enc.y);
	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	n = normalize(V3 * n);

	vpos = getPosView(viewRay, d, cameraProj);

	rayCast(n);
	vec3 o1 = normalize(tangent(n));
	vec3 o2 = (cross(o1, n));
	vec3 c1 = 0.5f * (o1 + o2);
	vec3 c2 = 0.5f * (o1 - o2);
	rayCast(mix(n, o1, angleMix));
	rayCast(mix(n, o2, angleMix));
	rayCast(mix(n, -c1, angleMix));
	rayCast(mix(n, -c2, angleMix));

	#ifdef _SSGICone9
	rayCast(mix(n, -o1, angleMix));
	rayCast(mix(n, -o2, angleMix));
	rayCast(mix(n, c1, angleMix));
	rayCast(mix(n, c2, angleMix));
	#endif

	#ifdef _RTGI
	fragColor.rgb = col;
	#endif
}
