#version 450

#include "compiled.glsl"
#include "std/gbuffer.glsl"
#include "std/math.glsl"
#include "std/shadows.glsl"

uniform sampler2D shadowMap;
uniform samplerCube shadowMapCube;
uniform sampler2D dilate;
// uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
// uniform sampler2D gbuffer1;
uniform vec2 cameraProj;
uniform float shadowsBias;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform mat4 LWVP;
uniform int lightShadow;
uniform vec2 lightProj;
uniform vec3 lightPos;

in vec2 texCoord;
in vec3 viewRay;

out float fragColor[2];

void main() {
	vec4 g0 = texture(gbuffer0, texCoord);
	// #ifdef _InvY // D3D
	// float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	// #else
	float depth = (1.0 - g0.a) * 2.0 - 1.0;
	// #endif
	vec3 p = getPos(eye, eyeLook, viewRay, depth, cameraProj);
	
	vec4 lightPosition = LWVP * vec4(p, 1.0);
	vec3 lPos = lightPosition.xyz / lightPosition.w;

	// Visibility
	if (lightShadow == 1) {
		float sm = texture(shadowMap, lPos.xy).r;
		fragColor[0] = float(sm + shadowsBias > lPos.z);

		// Distance
		float d = texture(dilate, lPos.xy).r;
		fragColor[1] = max((lPos.z - d), 0.0);
		fragColor[1] *= 100 * penumbraDistance;
	}
	else { // Cube
		vec3 lp = lightPos - p;
		vec3 l = normalize(lp);
		fragColor[0] = float(texture(shadowMapCube, -l).r + shadowsBias > lpToDepth(lp, lightProj));
		fragColor[1] = 0.0;
	}

	// Mask non-occluded pixels
	// fragColor.b = mask;
}
