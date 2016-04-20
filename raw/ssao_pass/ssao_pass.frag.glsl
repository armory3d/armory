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

uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
uniform sampler2D snoise;
uniform mat4 invVP;
uniform vec3 eye;

const float PI = 3.1415926535;
const vec2 screenSize = vec2(800.0, 600.0);
const vec2 aspectRatio = vec2(min(1.0, screenSize.y / screenSize.x), min(1.0, screenSize.x / screenSize.y));

const int kernelSize = 8;
const float aoSize = 0.04;
const float strength = 0.3;

in vec2 texCoord;

// float rand(vec2 co) { // Unreliable
//   return fract(sin(dot(co.xy ,vec2(12.9898, 78.233))) * 43758.5453);
// }
vec2 octahedronWrap(vec2 v) {
    return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}
vec3 getPos(float depth, vec2 coord) {	
    // vec4 pos = vec4(coord * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0);
    vec4 pos = vec4(coord * 2.0 - 1.0, depth, 1.0);
    pos = invVP * pos;
    pos.xyz /= pos.w;
    return pos.xyz - eye;
}

float doAO(vec2 kernelVec, vec2 randomVec, mat2 rotMat, vec3 currentPos, vec3 currentNormal, float currentDistance) {
	kernelVec.xy *= aspectRatio;
	float radius = aoSize * randomVec.y;
	kernelVec.xy = ((rotMat * kernelVec.xy) / currentDistance) * radius;
	vec2 coord = texCoord + kernelVec.xy;
	float depth = 1.0 - texture(gbuffer0, coord).a;
	vec3 pos = getPos(depth, coord) - currentPos;
	
	float angle = dot(pos, currentNormal);
	angle *= step(0.3, angle / length(pos)); // Fix intersect
	angle -= currentDistance * 0.001;
	angle = max(0.0, angle);
	angle /= dot(pos, pos) / min(currentDistance * 0.25, 1.0) + 0.00001; // Fix darkening
	return angle;
}

void main() {
	float depth = 1.0 - texture(gbuffer0, texCoord).a;
	if (depth == 0.0) {
		gl_FragColor = vec4(1.0);
		return;
	}
	
	vec2 kernel[kernelSize];		
 	kernel[0] = vec2(1.0, 0.0);		
 	kernel[1] = vec2(0.7071067, 0.7071067);		
 	kernel[2] = vec2(0.0, 1.0);		
 	kernel[3] = vec2(-0.7071067, 0.7071067);		
 	kernel[4] = vec2(-1.0, 0.0);		
 	kernel[5] = vec2(-0.7071067, -0.7071067);		
 	kernel[6] = vec2(0.0, -1.0);		
 	kernel[7] = vec2(0.7071067, -0.7071067);
	// kernel[0] = vec2(1.0, 0.0);
	// kernel[1] = vec2(0.8660254, 0.4999999);
	// kernel[2] = vec2(0.5, 0.8660254);
	// kernel[3] = vec2(0.0, 1.0);
	// kernel[4] = vec2(-0.4999999, 0.8660254);
	// kernel[5] = vec2(-0.8660254, 0.5);
	// kernel[6] = vec2(-1.0, 0.0);
	// kernel[7] = vec2(-0.8660254, -0.4999999);
	// kernel[8] = vec2(-0.5, -0.8660254);
	// kernel[9] = vec2(0.0, -1.0);
	// kernel[10] = vec2(0.4999999, -0.8660254);
	// kernel[11] = vec2(0.8660254, -0.5);
	
	vec2 enc = texture(gbuffer0, texCoord).rg;      
    vec3 currentNormal;
    currentNormal.z = 1.0 - abs(enc.x) - abs(enc.y);
    currentNormal.xy = currentNormal.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	currentNormal = normalize(currentNormal);
	
	vec3 currentPos = getPos(depth, texCoord);
	float currentDistance = length(currentPos);
	
	vec2 randomVec = texture(snoise, (texCoord * screenSize) / 8.0).xy;
	randomVec = randomVec * 2.0 - 1.0;
	mat2 rotMat = mat2(vec2(cos(randomVec.x * PI), -sin(randomVec.x * PI)),
					   vec2(sin(randomVec.x * PI), cos(randomVec.x * PI)));
	
	float amount = 0.0;
	// for (int i = 0; i < kernelSize; i++) {
		amount += doAO(kernel[0], randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel[1], randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel[2], randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel[3], randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel[4], randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel[5], randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel[6], randomVec, rotMat, currentPos, currentNormal, currentDistance);
		amount += doAO(kernel[7], randomVec, rotMat, currentPos, currentNormal, currentDistance);
	// }
	
	amount *= strength / kernelSize;
	amount = 1.0 - amount;
	amount = max(0.0, amount);
    gl_FragColor = vec4(vec3(amount), 1.0);
}
