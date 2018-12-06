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

#include "compiled.inc"
#include "std/gbuffer.glsl"

const int kernelSize = 12;
const vec2 kernel[12] = vec2[] (
	vec2(1.0, 0.0),
	vec2(0.8660254, 0.4999999),
	vec2(0.5, 0.8660254),
	vec2(0.0, 1.0),
	vec2(-0.4999999, 0.8660254),
	vec2(-0.8660254, 0.5),
	vec2(-1.0, 0.0),
	vec2(-0.8660254, -0.4999999),
	vec2(-0.5, -0.8660254),
	vec2(0.0, -1.0),
	vec2(0.4999999, -0.8660254),
	vec2(0.8660254, -0.5)
);

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D snoise;
uniform vec2 cameraProj;
uniform vec3 eyeLook;
uniform vec2 screenSize;
uniform vec2 aspectRatio;

in vec2 texCoord;
in vec3 viewRay;
out float fragColor;

void main() {
	float depth = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
	if (depth == 1.0) { fragColor = 1.0; return; }

	vec2 enc = textureLod(gbuffer0, texCoord, 0.0).rg;      
	vec3 n;
	n.z = 1.0 - abs(enc.x) - abs(enc.y);
	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	n = normalize(n);
	
	vec3 vray = normalize(viewRay);
	vec3 currentPos = getPosNoEye(eyeLook, vray, depth, cameraProj);
	float currentDistance = length(currentPos);
	float currentDistanceA = currentDistance * 0.002;
	float currentDistanceB = min(currentDistance * 0.25, 1.0);
	
	vec2 randomVec = textureLod(snoise, (texCoord * screenSize) / 8.0, 0.0).xy * 2.0 - 1.0;
	mat2 rotMat = mat2(vec2(cos(randomVec.x * PI), -sin(randomVec.x * PI)),
					   vec2(sin(randomVec.x * PI), cos(randomVec.x * PI)));
	float radius = ssaoSize * randomVec.y;

	fragColor = 0;
	for (int i = 0; i < 12; ++i) {
		vec2 k = ((rotMat * kernel[i] * aspectRatio) / currentDistance) * radius;
		depth = textureLod(gbufferD, texCoord + k, 0.0).r * 2.0 - 1.0;
		vec3 pos = getPosNoEye(eyeLook, vray, depth, cameraProj) - currentPos;
		
		float angle = dot(pos, n);
		angle *= step(0.1, angle / length(pos)); // Fix intersect
		angle -= currentDistanceA;
		angle = max(0.0, angle);
		angle /= dot(pos, pos) / currentDistanceB + 0.015; // Fix darkening
		fragColor += angle;
	}
	
	fragColor *= ssaoStrength / kernelSize;
	fragColor = 1.0 - fragColor;
}
