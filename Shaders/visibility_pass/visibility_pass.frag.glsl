#version 450

#include "../compiled.glsl"
#include "../std/gbuffer.glsl"
#include "../std/math.glsl"

uniform sampler2D shadowMap;
uniform sampler2D dilate;
// uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
// uniform sampler2D gbuffer1;
uniform vec2 cameraProj;
uniform float shadowsBias;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform mat4 LWVP;
// uniform int lightShadow;

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
	
	vec4 lampPos = LWVP * vec4(p, 1.0);
	vec3 lPos = lampPos.xyz / lampPos.w;

	// Visibility
	// if (lightShadow == 1) {
		float sm = texture(shadowMap, lPos.xy).r;
    	fragColor[0] = float(sm + shadowsBias > lPos.z);
	// }
	// else if (lightShadow == 2) { // Cube
		// visibility = PCFCube(lp, -l, shadowsBias, lightProj, n);
	// }
    
    // Distance
    float d = texture(dilate, lPos.xy).r;
    fragColor[1] = max((lPos.z - d), 0.0);
    fragColor[1] *= 100 * penumbraDistance;

    // Mask non-occluded pixels
    // fragColor.b = mask;
}
