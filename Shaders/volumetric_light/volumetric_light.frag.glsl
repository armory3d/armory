// http://sebastien.hillaire.free.fr/index.php?option=com_content&view=article&id=72&Itemid=106
#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "compiled.glsl"
#include "std/gbuffer.glsl"
#include "std/shadows.glsl"

uniform sampler2D gbufferD;
#ifndef _NoShadows
	//!uniform sampler2D shadowMap;
	//!uniform samplerCube shadowMapCube;
#endif
uniform sampler2D snoise;

uniform vec2 screenSize;
uniform mat4 invVP;
uniform mat4 LWVP;
uniform vec3 eye;
uniform vec3 lightPos;
uniform vec3 lightColor;
uniform float lightRadius;
uniform float shadowsBias;
uniform int lightShadow;
uniform vec2 lightPlane;

in vec4 wvpposition;
out vec4 fragColor;

const float tScat = 0.08;
const float tAbs = 0.0;
const float tExt = 0.0; //tScat + tAbs;
// const float stepLen = 1.0 / 11.0;
const float stepLen = 1.0 / 80; // Temporary..

// const float lighting = 0.4;
float lighting(vec3 p) {
	vec3 L = lightPos.xyz - p.xyz;
	float Ldist = length(lightPos.xyz - p.xyz);
	vec3 Lnorm = L / Ldist;

	float linearAtenuation = min(1.0, max(0.0, (lightRadius - Ldist) / lightRadius));
	return linearAtenuation; //* min(1.0, 1.0 / (Ldist * Ldist));
}

void rayStep(inout vec3 curPos, inout float curOpticalDepth, inout float scatteredLightAmount, float stepLenWorld, vec3 viewVecNorm) {
	curPos += stepLenWorld * viewVecNorm;
	float density = 1.0;
	
	float l1 = lighting(curPos) * stepLenWorld * tScat * density;
	curOpticalDepth *= exp(-tExt * stepLenWorld * density);
	// vec3 lightDir = (lightPos - curPos);
	// vec3 lightDirNorm = -normalize(lightDir);

	float visibility = 1.0;
	vec4 lampPos = LWVP * vec4(curPos, 1.0);
	if (lampPos.w > 0.0) {
		lampPos.xyz /= lampPos.w;
		visibility = float(texture(shadowMap, lampPos.xy).r > lampPos.z - shadowsBias);
	}
	
	// Cubemap
	// visibility = float(texture(shadowMapCube, -l).r + shadowsBias > lpToDepth(lp, lightPlane));

	scatteredLightAmount += curOpticalDepth * l1 * visibility;
}

void main() {
	vec2 screenPosition = wvpposition.xy / wvpposition.w;
	vec2 texCoord = screenPosition * 0.5 + 0.5;
	// texCoord += vec2(0.5 / screenSize); // Half pixel offset

	float pixelRayMarchNoise = texture(snoise, texCoord).r;

	float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	vec3 worldPos = getPos2(invVP, depth, texCoord);

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

	curPos += stepLenWorld * viewVecNorm * (2.0 * pixelRayMarchNoise - 1.0);

	// for(float l = stepLen; l < 0.99999; l += stepLen) {// Do not do the first and last steps
		// Raw steps for now..
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);

		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);

		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);



		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);

		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);


		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);

		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
		rayStep(curPos, curOpticalDepth, scatteredLightAmount, stepLenWorld, viewVecNorm);
	// }

	// curOpticalDepth
	fragColor = vec4(vec3(scatteredLightAmount * volumAirColor * normalize(lightColor.rgb) * volumAirTurbidity), 0.0); // * ((1.0 - depth) * 10.0)
}
