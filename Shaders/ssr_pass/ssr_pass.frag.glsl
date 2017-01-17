#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"
#include "../std/math.glsl"
// rand()
#include "../std/gbuffer.glsl"
// octahedronWrap()
// unpackFloat()

uniform sampler2D tex;
uniform sampler2D gbufferD;
uniform sampler2D gbuffer0; // Normal, roughness
uniform mat4 P;
uniform mat4 tiV;

// const int maxSteps = 20;
// const int numBinarySearchSteps = 5;
// const float ssrRayStep = 0.04;
// const float ssrMinRayStep = 0.05;
// const float ssrSearchDist = 5.0;
// const float ssrFalloffExp = 5.0;
// const float ssrJitter = 0.6;

in vec3 viewRay;
in vec2 texCoord;
out vec4 fragColor;

vec3 hitCoord;
float depth;

vec2 getProjectedCoord(vec3 hitCoord) {
	vec4 projectedCoord = P * vec4(hitCoord, 1.0);
	projectedCoord.xy /= projectedCoord.w;
	projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
	return projectedCoord.xy;
}

float getDeltaDepth(vec3 hitCoord) {	
	// depth = 1.0 - texture(gbuffer0, getProjectedCoord(hitCoord)).a;
	depth = texture(gbufferD, getProjectedCoord(hitCoord)).r * 2.0 - 1.0;
	vec3 viewPos = getPosView(viewRay, depth);
	return viewPos.z - hitCoord.z;
}

vec4 binarySearch(vec3 dir) {	
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
		dir *= 0.5;
		hitCoord -= dir;
		if (getDeltaDepth(hitCoord) < 0.0) hitCoord += dir;
		dir *= 0.5;
		hitCoord -= dir;
		if (getDeltaDepth(hitCoord) < 0.0) hitCoord += dir;
		////
		// dir *= 0.5;
		// hitCoord -= dir;
		// if (getDeltaDepth(hitCoord) < 0.0) hitCoord += dir;
		// dir *= 0.5;
		// hitCoord -= dir;
		// if (getDeltaDepth(hitCoord) < 0.0) hitCoord += dir;
		// dir *= 0.5;
		// hitCoord -= dir;
		// if (getDeltaDepth(hitCoord) < 0.0) hitCoord += dir;
		// dir *= 0.5;
		// hitCoord -= dir;
		// if (getDeltaDepth(hitCoord) < 0.0) hitCoord += dir;
		// dir *= 0.5;
		// hitCoord -= dir;
		// if (getDeltaDepth(hitCoord) < 0.0) hitCoord += dir;
		// dir *= 0.5;
		// hitCoord -= dir;
		// if (getDeltaDepth(hitCoord) < 0.0) hitCoord += dir;
		
		// Ugly discard of hits too far away
		if (abs(getDeltaDepth(hitCoord)) > 0.01) {
			return vec4(0.0);
		}
	// }
	return vec4(getProjectedCoord(hitCoord), 0.0, 1.0);
}

vec4 rayCast(vec3 dir) {
	dir *= ssrRayStep;
	
	// for (int i = 0; i < maxSteps; i++) {
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		////
		// hitCoord += dir;
		// if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		// hitCoord += dir;
		// if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		// hitCoord += dir;
		// if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		// hitCoord += dir;
		// if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		// hitCoord += dir;
		// if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		// hitCoord += dir;
		// if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		// hitCoord += dir;
		// if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		// hitCoord += dir;
		// if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		// hitCoord += dir;
		// if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		// hitCoord += dir;
		// if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		// hitCoord += dir;
		// if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
		// hitCoord += dir;
		// if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
	// }
	return vec4(0.0, 0.0, 0.0, 0.0);
}

void main() {

	vec4 g0 = texture(gbuffer0, texCoord);
	float roughness = unpackFloat(g0.b).y;

	if (roughness == 1.0) {
		fragColor = vec4(0.0);
		return;
	}
	float reflectivity = 1.0 - roughness;
	
	float d = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	if (d == 1.0) {
		fragColor = vec4(0.0);
		return;
	}

	vec2 enc = g0.rg;
	vec3 n;
	n.z = 1.0 - abs(enc.x) - abs(enc.y);
	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	n = normalize(n);
	
	vec4 viewNormal = vec4(n, 1.0);
	
	if (viewNormal.z <= 0.9) {
		fragColor = vec4(0.0);
		return; // Only up facing surfaces for now
	}

	viewNormal = tiV * normalize(viewNormal);
	vec3 viewPos = getPosView(viewRay, d);
	
	vec3 reflected = normalize(reflect((viewPos.xyz), normalize(viewNormal.xyz)));
	hitCoord = viewPos.xyz;
	
	vec3 dir = reflected * max(ssrMinRayStep, -viewPos.z) * (1.0 - rand(texCoord) * ssrJitter * roughness);
	vec4 coords = rayCast(dir);

	vec2 deltaCoords = abs(vec2(0.5, 0.5) - coords.xy);
	float screenEdgeFactor = clamp(1.0 - (deltaCoords.x + deltaCoords.y), 0.0, 1.0);

	float intensity = pow(reflectivity, ssrFalloffExp) *
		screenEdgeFactor * clamp(-reflected.z, 0.0, 1.0) *
		clamp((ssrSearchDist - length(viewPos.xyz - hitCoord)) * (1.0 / ssrSearchDist), 0.0, 1.0) * coords.w;

	// vec4 texColor = texture(tex, texCoord);
	// float brightness = dot(texColor.rgb, vec3(0.2126, 0.7152, 0.0722));
	// intensity *= min(brightness, 1.0);
	intensity = clamp(intensity, 0.0, 1.0);
	
	if (intensity == 0.0) {
		fragColor = vec4(0.0);
		return;
	}
	
	vec4 reflCol = vec4(texture(tex, coords.xy).rgb, 1.0);
	reflCol = clamp(reflCol, 0.0, 1.0);
	// fragColor = texColor * (1.0 - intensity) + reflCol * intensity;
	fragColor = reflCol * intensity * 0.5; //
}
