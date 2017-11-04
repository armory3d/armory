#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"
#include "../std/gbuffer.glsl"

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
uniform vec2 cameraProj;

in vec2 texCoord;
in vec3 viewRay;
out vec4 fragColor;

float doAO(vec2 kernelVec, vec2 randomVec, mat2 rotMat, vec3 currentPos, vec3 n, float currentDistance) {
	kernelVec.xy *= aspectRatio;
	float radius = ssaoSize * randomVec.y;
	kernelVec.xy = ((rotMat * kernelVec.xy) / currentDistance) * radius;
	vec2 coord = texCoord + kernelVec.xy;
	float depth = texture(gbufferD, coord).r * 2.0 - 1.0;
	vec3 pos = getPosNoEye(eyeLook, viewRay, depth, cameraProj) - currentPos;
	
	float angle = dot(pos, n);
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
		fragColor.r = 1.0;
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
	vec3 n;
	n.z = 1.0 - abs(enc.x) - abs(enc.y);
	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	n = normalize(n);
	
	vec3 currentPos = getPosNoEye(eyeLook, viewRay, depth, cameraProj);
	float currentDistance = length(currentPos);
	
	vec2 randomVec = texture(snoise, (texCoord * screenSize) / 8.0).xy;
	randomVec = randomVec * 2.0 - 1.0;
	mat2 rotMat = mat2(vec2(cos(randomVec.x * PI), -sin(randomVec.x * PI)),
					   vec2(sin(randomVec.x * PI), cos(randomVec.x * PI)));
	
	// for (int i = 0; i < kernelSize; i++) {
		fragColor.r = doAO(kernel0, randomVec, rotMat, currentPos, n, currentDistance);
		fragColor.r += doAO(kernel1, randomVec, rotMat, currentPos, n, currentDistance);
		fragColor.r += doAO(kernel2, randomVec, rotMat, currentPos, n, currentDistance);
		fragColor.r += doAO(kernel3, randomVec, rotMat, currentPos, n, currentDistance);
		fragColor.r += doAO(kernel4, randomVec, rotMat, currentPos, n, currentDistance);
		fragColor.r += doAO(kernel5, randomVec, rotMat, currentPos, n, currentDistance);
		fragColor.r += doAO(kernel6, randomVec, rotMat, currentPos, n, currentDistance);
		fragColor.r += doAO(kernel7, randomVec, rotMat, currentPos, n, currentDistance);
		fragColor.r += doAO(kernel8, randomVec, rotMat, currentPos, n, currentDistance);
		fragColor.r += doAO(kernel9, randomVec, rotMat, currentPos, n, currentDistance);
		fragColor.r += doAO(kernel10, randomVec, rotMat, currentPos, n, currentDistance);
		fragColor.r += doAO(kernel11, randomVec, rotMat, currentPos, n, currentDistance);
		// fragColor.r += doAO(kernel12, randomVec, rotMat, currentPos, n, currentDistance);
		// fragColor.r += doAO(kernel13, randomVec, rotMat, currentPos, n, currentDistance);
		// fragColor.r += doAO(kernel14, randomVec, rotMat, currentPos, n, currentDistance);
		// fragColor.r += doAO(kernel15, randomVec, rotMat, currentPos, n, currentDistance);
		// fragColor.r += doAO(kernel16, randomVec, rotMat, currentPos, n, currentDistance);
		// fragColor.r += doAO(kernel17, randomVec, rotMat, currentPos, n, currentDistance);
		// fragColor.r += doAO(kernel18, randomVec, rotMat, currentPos, n, currentDistance);
		// fragColor.r += doAO(kernel19, randomVec, rotMat, currentPos, n, currentDistance);
	// }
	
	fragColor.r *= ssaoStrength / kernelSize;
	fragColor.r = max(0.0, 1.0 - fragColor.r);

	// Velocity is assumed to be calculated for motion blur, so we need to inverse it for reprojection
	vec2 velocity = -textureLod(sveloc, texCoord, 0.0).rg;
	float last = texture(slast, texCoord + velocity).r;
	fragColor.r = (fragColor.r + last) * 0.5;
}
