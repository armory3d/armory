// http://sebastien.hillaire.free.fr/index.php?option=com_content&view=article&id=72&Itemid=106
#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"
#include "std/shadows.glsl"

uniform sampler2D gbufferD;
#ifndef _NoShadows
uniform sampler2D shadowMap;
#endif
uniform sampler2D snoise;

#ifdef _CSM
	//!uniform vec4 casData[shadowmapCascades * 4 + 4];
#else
	uniform mat4 LWVP;
#endif
uniform float shadowsBias;
// uniform vec3 lightPos;
uniform vec3 lightColor;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform vec2 cameraProj;
// uniform float lightRadius;
// uniform int lightShadow;
// uniform vec2 lightPlane;

in vec2 texCoord;
in vec3 viewRay;
out float fragColor;

const float tScat = 0.08;
const float tAbs = 0.0;
const float tExt = tScat + tAbs;
const float stepLen = 1.0 / volumSteps;
const float lighting = 0.4;
// float lighting(vec3 p) {
	// vec3 L = lightPos.xyz - p.xyz;
	// float Ldist = length(lightPos.xyz - p.xyz);
	// vec3 Lnorm = L / Ldist;

	// float linearAtenuation = min(1.0, max(0.0, (lightRadius - Ldist) / lightRadius));
	// return linearAtenuation; //* min(1.0, 1.0 / (Ldist * Ldist));
// }

void rayStep(inout vec3 curPos, inout float curOpticalDepth, inout float scatteredLightAmount, float stepLenWorld, vec3 viewVecNorm) {
	curPos += stepLenWorld * viewVecNorm;
	const float density = 1.0;
	
	// float l1 = lighting(curPos) * stepLenWorld * tScat * density;
	float l1 = lighting * stepLenWorld * tScat * density;
	curOpticalDepth *= exp(-tExt * stepLenWorld * density);

	float visibility = 1.0;
	#ifdef _CSM
    mat4 LWVP = mat4(casData[4 + 0], casData[4 + 1], casData[4 + 2], casData[4 + 3]);
	#endif
	vec4 lightPosition = LWVP * vec4(curPos, 1.0);
	if (lightPosition.w > 0.0) {
		lightPosition.xyz /= lightPosition.w;
		visibility = float(texture(shadowMap, lightPosition.xy).r > lightPosition.z - shadowsBias);
	}

	scatteredLightAmount += curOpticalDepth * l1 * visibility;
}

void main() {

	float pixelRayMarchNoise = texture(snoise, texCoord * 100).r * 2.0 - 1.0;

	float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	vec3 worldPos = getPos(eye, eyeLook, viewRay, depth, cameraProj);

	vec3 viewVec = worldPos - eye;
	float worldPosDist = length(viewVec);
	vec3 viewVecNorm = viewVec / worldPosDist;

	float startDepth = 0.1;
	startDepth = min(worldPosDist, startDepth);
	float endDepth = 20.0;
	endDepth = min(worldPosDist, endDepth);

	vec3 curPos = eye + viewVecNorm * startDepth;
	float stepLenWorld = stepLen * (endDepth - startDepth);
	float curOpticalDepth = exp(-tExt * stepLenWorld);
	float scatteredLightAmount = 0.0;

	curPos += stepLenWorld * viewVecNorm * pixelRayMarchNoise;

	for (float l = stepLen; l < 0.99999; l += stepLen) { // Do not do the first and last steps
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
	}

	fragColor = scatteredLightAmount * volumAirTurbidity;
}
