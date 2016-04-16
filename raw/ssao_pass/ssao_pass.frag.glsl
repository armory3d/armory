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
uniform sampler2D gbuffer2;
uniform sampler2D snoise;

const float PI = 3.1415926535;
// const vec2 screenSize = vec2(800.0, 600.0);
const vec2 screenSize = vec2(1920.0, 1080.0);
const float aoSize = 0.6;//0.43;
const int kernelSize = 8;
const float strength = 0.8;//0.55;

in vec2 texCoord;

float linearize(float depth, float znear, float zfar) {
	return -zfar * znear / (depth * (zfar - znear) - zfar);
}

// float rand(vec2 co) { // Unreliable
//   return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
// }

vec2 octahedronWrap(vec2 v) {
    return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}

void main() {	
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
	
	vec4 g0 = texture(gbuffer0, texCoord);      
	vec4 g1 = texture(gbuffer1, texCoord);
	
	// vec2 enc = g0.rg;
    // vec3 N;
    // N.z = 1.0 - abs(enc.x) - abs(enc.y);
    // N.xy = N.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
    // N = normalize(N);
	
	vec3 N = g0.rgb; 
	vec3 P = g1.rgb;
	
	// Get the current pixel's positiom
	vec3 currentPos = P;
	// float currentDistance = length(currentPos);
	float currentDistance = linearize(g0.a, 0.1, 1000.0);
	vec3 currentNormal = N;
	
	vec2 aspectRatio = vec2(min(1.0, screenSize.y / screenSize.x), min(1.0, screenSize.x / screenSize.y));
	
	// Grab a random vector from a 8x8 tiled random texture
	// vec2 randomVec = vec2(rand(texCoord), rand(texCoord * 2.0));
	vec2 randomVec = texture(snoise, (0.5 * texCoord * screenSize) / 8.0).xy;
	randomVec *= 2.0;
	randomVec -= 1.0;
	mat2 rotMat = mat2( vec2( cos( randomVec.x * PI ), -sin( randomVec.x * PI ) ),
						vec2( sin( randomVec.x * PI ), cos( randomVec.x * PI ) ) );
	
	float amount = 0.0;
	
	// for (int i = 0; i < kernelSize; i++) {
		vec2 kernelVec = kernel[0];
		kernelVec.xy *= aspectRatio;
		float radius = aoSize * randomVec.y;
		kernelVec.xy = (rotMat * kernelVec.xy);
		kernelVec.xy = (kernelVec.xy / currentDistance) * radius;
		vec3 pos = texture(gbuffer1, texCoord + kernelVec.xy).rgb;
		pos = pos - currentPos;
		
		float angle = dot(pos, currentNormal);
		angle *= step(0.3, angle / length(pos)); // Fix intersect
		angle -= currentDistance * 0.001;
		angle = max(0.0, angle);
		angle /= dot(pos, pos) + 0.00001; // Fix darkening
		// angle /= dot( pos, pos ) / min( currentDistance * 0.25, 1.0 ) + 0.00001;
		amount += angle;
		
		
		kernelVec = kernel[1];
		kernelVec.xy *= aspectRatio;
		radius = aoSize * randomVec.y;
		kernelVec.xy = (rotMat * kernelVec.xy);
		kernelVec.xy = (kernelVec.xy / currentDistance) * radius;
		pos = texture(gbuffer1, texCoord + kernelVec.xy).rgb;
		pos = pos - currentPos;
		
		angle = dot(pos, currentNormal);
		angle *= step(0.3, angle / length(pos)); // Fix intersect
		angle -= currentDistance * 0.001;
		angle = max(0.0, angle);
		angle /= dot(pos, pos) + 0.00001; // Fix darkening
		// angle /= dot( pos, pos ) / min( currentDistance * 0.25, 1.0 ) + 0.00001;
		amount += angle;
		
		
		kernelVec = kernel[2];
		kernelVec.xy *= aspectRatio;
		radius = aoSize * randomVec.y;
		kernelVec.xy = (rotMat * kernelVec.xy);
		kernelVec.xy = (kernelVec.xy / currentDistance) * radius;
		pos = texture(gbuffer1, texCoord + kernelVec.xy).rgb;
		pos = pos - currentPos;
		
		angle = dot(pos, currentNormal);
		angle *= step(0.3, angle / length(pos)); // Fix intersect
		angle -= currentDistance * 0.001;
		angle = max(0.0, angle);
		angle /= dot(pos, pos) + 0.00001; // Fix darkening
		// angle /= dot( pos, pos ) / min( currentDistance * 0.25, 1.0 ) + 0.00001;
		amount += angle;
		
		
		kernelVec = kernel[3];
		kernelVec.xy *= aspectRatio;
		radius = aoSize * randomVec.y;
		kernelVec.xy = (rotMat * kernelVec.xy);
		kernelVec.xy = (kernelVec.xy / currentDistance) * radius;
		pos = texture(gbuffer1, texCoord + kernelVec.xy).rgb;
		pos = pos - currentPos;
		
		angle = dot(pos, currentNormal);
		angle *= step(0.3, angle / length(pos)); // Fix intersect
		angle -= currentDistance * 0.001;
		angle = max(0.0, angle);
		angle /= dot(pos, pos) + 0.00001; // Fix darkening
		// angle /= dot( pos, pos ) / min( currentDistance * 0.25, 1.0 ) + 0.00001;
		amount += angle;
		
		
		kernelVec = kernel[4];
		kernelVec.xy *= aspectRatio;
		radius = aoSize * randomVec.y;
		kernelVec.xy = (rotMat * kernelVec.xy);
		kernelVec.xy = (kernelVec.xy / currentDistance) * radius;
		pos = texture(gbuffer1, texCoord + kernelVec.xy).rgb;
		pos = pos - currentPos;
		
		angle = dot(pos, currentNormal);
		angle *= step(0.3, angle / length(pos)); // Fix intersect
		angle -= currentDistance * 0.001;
		angle = max(0.0, angle);
		angle /= dot(pos, pos) + 0.00001; // Fix darkening
		// angle /= dot( pos, pos ) / min( currentDistance * 0.25, 1.0 ) + 0.00001;
		amount += angle;
		
		
		kernelVec = kernel[5];
		kernelVec.xy *= aspectRatio;
		radius = aoSize * randomVec.y;
		kernelVec.xy = (rotMat * kernelVec.xy);
		kernelVec.xy = (kernelVec.xy / currentDistance) * radius;
		pos = texture(gbuffer1, texCoord + kernelVec.xy).rgb;
		pos = pos - currentPos;
		
		angle = dot(pos, currentNormal);
		angle *= step(0.3, angle / length(pos)); // Fix intersect
		angle -= currentDistance * 0.001;
		angle = max(0.0, angle);
		angle /= dot(pos, pos) + 0.00001; // Fix darkening
		// angle /= dot( pos, pos ) / min( currentDistance * 0.25, 1.0 ) + 0.00001;
		amount += angle;
		
		
		kernelVec = kernel[6];
		kernelVec.xy *= aspectRatio;
		radius = aoSize * randomVec.y;
		kernelVec.xy = (rotMat * kernelVec.xy);
		kernelVec.xy = (kernelVec.xy / currentDistance) * radius;
		pos = texture(gbuffer1, texCoord + kernelVec.xy).rgb;
		pos = pos - currentPos;
		
		angle = dot(pos, currentNormal);
		angle *= step(0.3, angle / length(pos)); // Fix intersect
		angle -= currentDistance * 0.001;
		angle = max(0.0, angle);
		angle /= dot(pos, pos) + 0.00001; // Fix darkening
		// angle /= dot( pos, pos ) / min( currentDistance * 0.25, 1.0 ) + 0.00001;
		amount += angle;
		
		
		kernelVec = kernel[7];
		kernelVec.xy *= aspectRatio;
		radius = aoSize * randomVec.y;
		kernelVec.xy = (rotMat * kernelVec.xy);
		kernelVec.xy = (kernelVec.xy / currentDistance) * radius;
		pos = texture(gbuffer1, texCoord + kernelVec.xy).rgb;
		pos = pos - currentPos;
		
		angle = dot(pos, currentNormal);
		angle *= step(0.3, angle / length(pos)); // Fix intersect
		angle -= currentDistance * 0.001;
		angle = max(0.0, angle);
		angle /= dot(pos, pos) + 0.00001; // Fix darkening
		// angle /= dot( pos, pos ) / min( currentDistance * 0.25, 1.0 ) + 0.00001;
		amount += angle;
		
		/*
		kernelVec = kernel[8];
		kernelVec.xy *= aspectRatio;
		radius = aoSize * randomVec.y;
		kernelVec.xy = (rotMat * kernelVec.xy);
		kernelVec.xy = (kernelVec.xy / currentDistance) * radius;
		pos = texture(gbuffer1, texCoord + kernelVec.xy).rgb;
		pos = pos - currentPos;
		
		angle = dot(pos, currentNormal);
		angle *= step(0.3, angle / length(pos)); // Fix intersect
		angle -= currentDistance * 0.001;
		angle = max(0.0, angle);
		angle /= dot(pos, pos) + 0.00001; // Fix darkening
		// angle /= dot( pos, pos ) / min( currentDistance * 0.25, 1.0 ) + 0.00001;
		amount += angle;
		
		
		kernelVec = kernel[9];
		kernelVec.xy *= aspectRatio;
		radius = aoSize * randomVec.y;
		kernelVec.xy = (rotMat * kernelVec.xy);
		kernelVec.xy = (kernelVec.xy / currentDistance) * radius;
		pos = texture(gbuffer1, texCoord + kernelVec.xy).rgb;
		pos = pos - currentPos;
		
		angle = dot(pos, currentNormal);
		angle *= step(0.3, angle / length(pos)); // Fix intersect
		angle -= currentDistance * 0.001;
		angle = max(0.0, angle);
		angle /= dot(pos, pos) + 0.00001; // Fix darkening
		// angle /= dot( pos, pos ) / min( currentDistance * 0.25, 1.0 ) + 0.00001;
		amount += angle;
		
		
		kernelVec = kernel[10];
		kernelVec.xy *= aspectRatio;
		radius = aoSize * randomVec.y;
		kernelVec.xy = (rotMat * kernelVec.xy);
		kernelVec.xy = (kernelVec.xy / currentDistance) * radius;
		pos = texture(gbuffer1, texCoord + kernelVec.xy).rgb;
		pos = pos - currentPos;
		
		angle = dot(pos, currentNormal);
		angle *= step(0.3, angle / length(pos)); // Fix intersect
		angle -= currentDistance * 0.001;
		angle = max(0.0, angle);
		angle /= dot(pos, pos) + 0.00001; // Fix darkening
		// angle /= dot( pos, pos ) / min( currentDistance * 0.25, 1.0 ) + 0.00001;
		amount += angle;
		
		
		kernelVec = kernel[11];
		kernelVec.xy *= aspectRatio;
		radius = aoSize * randomVec.y;
		kernelVec.xy = (rotMat * kernelVec.xy);
		kernelVec.xy = (kernelVec.xy / currentDistance) * radius;
		pos = texture(gbuffer1, texCoord + kernelVec.xy).rgb;
		pos = pos - currentPos;
		
		angle = dot(pos, currentNormal);
		angle *= step(0.3, angle / length(pos)); // Fix intersect
		angle -= currentDistance * 0.001;
		angle = max(0.0, angle);
		angle /= dot(pos, pos) + 0.00001; // Fix darkening
		// angle /= dot( pos, pos ) / min( currentDistance * 0.25, 1.0 ) + 0.00001;
		amount += angle;*/
	// }
	
	amount *= strength / kernelSize;
	amount = 1.0 - amount;
	amount = max(0.0, amount);
    gl_FragColor = vec4(vec3(amount), 1.0);
}
