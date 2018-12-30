// http://sebastien.hillaire.free.fr/index.php?option=com_content&view=article&id=72&Itemid=106
#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D gbufferD;
uniform sampler2DShadow shadowMap;
uniform sampler2D snoise;

#ifdef _CSM
	//!uniform vec4 casData[shadowmapCascades * 4 + 4];
#else
	uniform mat4 LWVP;
#endif
uniform float shadowsBias;
uniform vec3 lightColor;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform vec2 cameraProj;

in vec2 texCoord;
in vec3 viewRay;
out float fragColor;

const float tScat = 0.08;
const float tAbs = 0.0;
const float tExt = tScat + tAbs;
const float stepLen = 1.0 / volumSteps;
const float lighting = 0.4;

void rayStep(inout vec3 curPos, inout float curOpticalDepth, inout float scatteredLightAmount, float stepLenWorld, vec3 viewVecNorm) {
	curPos += stepLenWorld * viewVecNorm;
	const float density = 1.0;
	
	float l1 = lighting * stepLenWorld * tScat * density;
	curOpticalDepth *= exp(-tExt * stepLenWorld * density);

	float visibility = 1.0;
	#ifdef _CSM
    mat4 LWVP = mat4(casData[4 + 0], casData[4 + 1], casData[4 + 2], casData[4 + 3]);
	#endif
	vec4 lightPosition = LWVP * vec4(curPos, 1.0);
	if (lightPosition.w > 0.0) {
		lightPosition.xyz /= lightPosition.w;
		visibility = texture(shadowMap, vec3(lightPosition.xy, lightPosition.z - shadowsBias));
	}

	scatteredLightAmount += curOpticalDepth * l1 * visibility;
}

void main() {

	float pixelRayMarchNoise = textureLod(snoise, texCoord * 100, 0.0).r * 2.0 - 1.0;

	float depth = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
	vec3 worldPos = getPos(eye, eyeLook, normalize(viewRay), depth, cameraProj);

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
