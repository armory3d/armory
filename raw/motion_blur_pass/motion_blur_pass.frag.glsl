// Based on GPU Gems 3
// http://http.developer.nvidia.com/GPUGems3/gpugems3_ch27.html
#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;

uniform sampler2D tex;
uniform mat4 prevVP;
uniform mat4 invVP;
uniform vec3 eye;
uniform vec3 eyeLook;

in vec3 viewRay;
in vec2 texCoord;

const int samples = 8;

vec3 getPos(float depth, vec2 coord) {	
	vec3 vray = normalize(viewRay);
	const float znear = 0.1;
	const float zfar = 1000.0;
	const float projectionA = zfar / (zfar - znear);
	const float projectionB = (-zfar * znear) / (zfar - znear);
	float linearDepth = projectionB / (depth * 0.5 + 0.5 - projectionA);
	float viewZDist = dot(eyeLook, vray);
	vec3 wposition = eye + vray * (linearDepth / viewZDist);
	return wposition;
}

vec2 getVelocity(vec2 coord, float depth) {
	vec4 currentPos = vec4(coord.xy * 2.0 - 1.0, depth, 1.0);
	vec4 worldPos = vec4(getPos(depth, coord), 1.0);
	vec4 previousPos = prevVP * worldPos;
	previousPos /= previousPos.w;
	vec2 velocity = (currentPos - previousPos).xy / 40.0;
	return velocity;
}

void main() {
	vec4 color = texture(tex, texCoord);
	
	// Do not blur masked objects
	if (texture(gbuffer0, texCoord).b == 1.0) {
		gl_FragColor = color;
		return;
	}
	
	float depth = 1.0 - texture(gbuffer0, texCoord).a;
	if (depth == 0.0) {
		gl_FragColor = color;
		return;
	}

	float blurScale = 1.0; //currentFps / targeFps;
	vec2 velocity = getVelocity(texCoord, depth) * blurScale * (-1.0);
	
	vec2 offset = texCoord;
	int processed = 1;
	// for(int i = 1; i < samples; ++i) {
		offset += velocity;
		if (texture(gbuffer0, offset).b != 1.0) {
   			color += texture(tex, offset);
			processed++;
		}

		offset += velocity;
		if (texture(gbuffer0, offset).b != 1.0) {
   			color += texture(tex, offset);
			processed++;
		}
		
		offset += velocity;
		if (texture(gbuffer0, offset).b != 1.0) {
   			color += texture(tex, offset);
			processed++;
		}
		
		offset += velocity;
		if (texture(gbuffer0, offset).b != 1.0) {
   			color += texture(tex, offset);
			processed++;
		}
		
		offset += velocity;
		if (texture(gbuffer0, offset).b != 1.0) {
   			color += texture(tex, offset);
			processed++;
		}
		
		offset += velocity;
		if (texture(gbuffer0, offset).b != 1.0) {
   			color += texture(tex, offset);
			processed++;
		}
		
		offset += velocity;
		if (texture(gbuffer0, offset).b != 1.0) {
   			color += texture(tex, offset);
			processed++;
		}
		
		offset += velocity;
		if (texture(gbuffer0, offset).b != 1.0) {
   			color += texture(tex, offset);
			processed++;
		}
	// }
	 
	vec4 finalColor = color / processed; 
	gl_FragColor = finalColor;
}
