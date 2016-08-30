// http://sebastien.hillaire.free.fr/index.php?option=com_content&view=article&id=72&Itemid=106
#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D gbufferD;
#ifndef _NoShadows
	uniform sampler2D shadowMap;
#endif
uniform sampler2D snoise;

uniform vec2 screenSize;
uniform mat4 invVP;
uniform mat4 LWVP;
uniform vec3 viewPos;
uniform vec3 lightPos;
uniform vec3 lightColor;
uniform float lightRadius;
uniform float lightStrength;
uniform float shadowsBias;

in vec4 wvpposition;
out vec4 outColor;

const float tScat = 0.08;
const float tAbs = 0.0;
const float tExt = 0.0; //tScat + tAbs;
// const float stepLen = 1.0 / 11.0;
const float stepLen = 1.0 / 80;

vec3 getPos(float depth, vec2 coord) {
    vec4 pos = vec4(coord * 2.0 - 1.0, depth, 1.0);
    pos = invVP * pos;
    pos.xyz /= pos.w;
    return pos.xyz;
}

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
	vec4 lPos = LWVP * vec4(curPos, 1.0);
	if (lPos.w > 0.0) {
		vec4 lPosH = lPos / lPos.w;
		lPosH.x = (lPosH.x + 1.0) / 2.0;
		lPosH.y = (lPosH.y + 1.0) / 2.0;
		float distanceFromLight = texture(shadowMap, lPosH.xy).r * 2.0 - 1.0;
		visibility = float(distanceFromLight > lPosH.z - shadowsBias);
	}

	scatteredLightAmount += curOpticalDepth * l1 * visibility;
}

void main() {
	vec2 screenPosition = wvpposition.xy / wvpposition.w;
	vec2 texCoord = screenPosition * 0.5 + 0.5;
	texCoord += vec2(0.5 / screenSize); // Half pixel offset

    float pixelRayMarchNoise = texture(snoise, texCoord).r;

	float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	vec3 worldPos = getPos(depth, texCoord);

	vec3 viewVec = worldPos - viewPos;
    float worldPosDist = length(viewVec);
    vec3 viewVecNorm = viewVec / worldPosDist;

    float startDepth = 0.1;
    startDepth = min(worldPosDist, startDepth);
    float endDepth = 20.0;
    endDepth = min(worldPosDist, endDepth);

    vec3 curPos = viewPos + viewVecNorm * startDepth;
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
	outColor = vec4(scatteredLightAmount * lightColor.rgb * lightStrength, 0.0);
}
