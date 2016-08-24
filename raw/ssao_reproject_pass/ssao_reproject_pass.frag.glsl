// Alchemy AO
// Compute kernel
// var kernel:Array<Float> = [];       
// var kernelSize = 8;
// for (i in 0...kernelSize) {
// 		var angle = i / kernelSize;
// 		angle *= 3.1415926535 * 2.0;
// 		var x1 = Math.cos(angle); 
// 		var y1 = Math.sin(angle);
// 		x1 = Std.int(x1 * 10000000) / 10000000;
// 		y1 = Std.int(y1 * 10000000) / 10000000;
// 		trace(x1, y1);
// }
#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D sveloc;
uniform sampler2D slast;
uniform sampler2D snoise;

uniform mat4 invVP;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform vec2 screenSize;
uniform vec2 aspectRatio;

#ifndef _SSAO // SSAO disabled, remove it from render path nodes to completely prevent generation
	const float ssaoSize = 0.03;
	const float ssaoStrength = 0.20;
#endif

in vec2 texCoord;
in vec3 viewRay;
out vec4 outColor;

// float rand(vec2 co) { // Unreliable
//   return fract(sin(dot(co.xy ,vec2(12.9898, 78.233))) * 43758.5453);
// }
vec2 octahedronWrap(vec2 v) {
    return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}
// vec3 getPos(float depth, vec2 coord) {	
//     vec4 pos = vec4(coord * 2.0 - 1.0, depth, 1.0);
//     pos = invVP * pos;
//     pos.xyz /= pos.w;
//     return pos.xyz - eye;
// }
vec3 getPos(float depth) {	
	vec3 vray = normalize(viewRay);
	const float projectionA = cameraPlane.y / (cameraPlane.y - cameraPlane.x);
	const float projectionB = -(cameraPlane.y * cameraPlane.x) / (cameraPlane.y - cameraPlane.x);
	float linearDepth = projectionB / (depth * 0.5 + 0.5 - projectionA);
	float viewZDist = dot(eyeLook, vray);
	// vec3 wposition = eye + vray * (linearDepth / viewZDist);
	vec3 wposition = vray * (linearDepth / viewZDist);
	return wposition;
}

float doAO(vec2 kernelVec, vec2 randomVec, mat2 rotMat, vec3 currentPos, vec3 currentNormal, float currentDistance) {
	kernelVec.xy *= aspectRatio;
	float radius = ssaoSize * randomVec.y;
	kernelVec.xy = ((rotMat * kernelVec.xy) / currentDistance) * radius;
	vec2 coord = texCoord + kernelVec.xy;
	float depth = texture(gbufferD, coord).r * 2.0 - 1.0;
	vec3 pos = getPos(depth) - currentPos;
	
	float angle = dot(pos, currentNormal);
	// angle *= step(0.3, angle / length(pos)); // Fix intersect
	angle *= step(0.1, angle / length(pos));
	angle -= currentDistance * 0.001;
	angle = max(0.0, angle);
	// angle /= dot(pos, pos) / min(currentDistance * 0.25, 1.0) + 0.00001; // Fix darkening
	angle /= dot(pos, pos) / min(currentDistance * 0.25, 1.0) + 0.001;
	return angle;
}

void main() {
	float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	if (depth == 1.0) {
		outColor = vec4(1.0);
		return;
	}
	
	const int kernelSize = 12;
	const vec2 kernel0 = vec2(1.0, 0.0);
	const vec2 kernel1 = vec2(0.8660254, 0.4999999);
	const vec2 kernel2 = vec2(0.5, 0.8660254);
	const vec2 kernel3 = vec2(0.0, 1.0);
	const vec2 kernel4 = vec2(-0.4999999, 0.8660254);
	const vec2 kernel5 = vec2(-0.8660254, 0.5);
	const vec2 kernel6 = vec2(-1.0, 0.0);
	const vec2 kernel7 = vec2(-0.8660254, -0.4999999);
	const vec2 kernel8 = vec2(-0.5, -0.8660254);
	const vec2 kernel9 = vec2(0.0, -1.0);
	const vec2 kernel10 = vec2(0.4999999, -0.8660254);
	const vec2 kernel11 = vec2(0.8660254, -0.5);
	// const vec2 kernel0 = vec2(1.0,0.0);
	// const vec2 kernel1 = vec2(0.9510565,0.3090169);
	// const vec2 kernel2 = vec2(0.8090169,0.5877852);
	// const vec2 kernel3 = vec2(0.5877852,0.8090169);
	// const vec2 kernel4 = vec2(0.3090169,0.9510565);
	// const vec2 kernel5 = vec2(0.0,1.0);
	// const vec2 kernel6 = vec2(-0.3090169,0.9510565);
	// const vec2 kernel7 = vec2(-0.5877852,0.8090169);
	// const vec2 kernel8 = vec2(-0.8090169,0.5877852);
	// const vec2 kernel9 = vec2(-0.9510565,0.3090169);
	// const vec2 kernel10 = vec2(-1,0);
	// const vec2 kernel11 = vec2(-0.9510565,-0.3090169);
	// const vec2 kernel12 = vec2(-0.8090169,-0.5877852);
	// const vec2 kernel13 = vec2(-0.5877852,-0.8090169);
	// const vec2 kernel14 = vec2(-0.3090169,-0.9510565);
	// const vec2 kernel15 = vec2(0.0,-1.0);
	// const vec2 kernel16 = vec2(0.3090169,-0.9510565);
	// const vec2 kernel17 = vec2(0.5877852,-0.8090169);
	// const vec2 kernel18 = vec2(0.8090169,-0.5877852);
	// const vec2 kernel19 = vec2(0.9510565,-0.3090169);

	vec2 enc = texture(gbuffer0, texCoord).rg;      
    vec3 currentNormal;
    currentNormal.z = 1.0 - abs(enc.x) - abs(enc.y);
    currentNormal.xy = currentNormal.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	currentNormal = normalize(currentNormal);
	
	vec3 currentPos = getPos(depth);
	float currentDistance = length(currentPos);
	
	vec2 randomVec = texture(snoise, (texCoord * screenSize) / 8.0).xy;
	randomVec = randomVec * 2.0 - 1.0;
	mat2 rotMat = mat2(vec2(cos(randomVec.x * PI), -sin(randomVec.x * PI)),
					   vec2(sin(randomVec.x * PI), cos(randomVec.x * PI)));
	
	// for (int i = 0; i < kernelSize; i++) {
		float amount = doAO(kernel0, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel1, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel2, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel3, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel4, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel5, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel6, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel7, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel8, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel9, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel10, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel11, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		// amount += doAO(kernel12, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		// amount += doAO(kernel13, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		// amount += doAO(kernel14, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		// amount += doAO(kernel15, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		// amount += doAO(kernel16, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		// amount += doAO(kernel17, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		// amount += doAO(kernel18, randomVec, rotMat, currentPos, currentNormal, currentDistance);
		// amount += doAO(kernel19, randomVec, rotMat, currentPos, currentNormal, currentDistance);
	// }
	
	amount *= ssaoStrength / kernelSize;
	amount = 1.0 - amount;
	amount = max(0.0, amount);
	// outColor = vec4(amount, 0.0, 0.0, 1.0);

	// Velocity is assumed to be calculated for motion blur, so we need to inverse it for reprojection
    vec2 velocity = -textureLod(sveloc, texCoord, 0.0).rg;
	float last = texture(slast, texCoord + velocity).r;
    outColor = vec4((amount + last) * 0.5, 0.0, 0.0, 1.0);
}
