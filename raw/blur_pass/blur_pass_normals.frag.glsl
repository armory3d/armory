#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;
uniform sampler2D gbuffer0;
uniform vec2 dir;

in vec2 texCoord;

void main() {
	float weights[9];
	weights[0] = 0.013519569015984728;
	weights[1] = 0.047662179108871855;
	weights[2] = 0.11723004402070096;
	weights[3] = 0.20116755999375591;
	weights[4] = 0.240841295721373;
	weights[5] = 0.20116755999375591;
	weights[6] = 0.11723004402070096;
	weights[7] = 0.047662179108871855;
	weights[8] = 0.013519569015984728;
	
	float indices[9];
	indices[0] = -4;
	indices[1] = -3;
	indices[2] = -2;
	indices[3] = -1;
	indices[4] = 0;
	indices[5] = 1;
	indices[6] = 2;
	indices[7] = 3;
	indices[8] = 4;

	vec2 step = dir / vec2(640, 480); //g_resolution.xy;
	
	vec3 normal[9];	
	normal[0] = texture(gbuffer0, texCoord + indices[0]*step).rgb * 2.0 - 1.0;
	normal[1] = texture(gbuffer0, texCoord + indices[1]*step).rgb * 2.0 - 1.0;
	normal[2] = texture(gbuffer0, texCoord + indices[2]*step).rgb * 2.0 - 1.0;
	normal[3] = texture(gbuffer0, texCoord + indices[3]*step).rgb * 2.0 - 1.0;
	normal[4] = texture(gbuffer0, texCoord + indices[4]*step).rgb * 2.0 - 1.0;
	normal[5] = texture(gbuffer0, texCoord + indices[5]*step).rgb * 2.0 - 1.0;
	normal[6] = texture(gbuffer0, texCoord + indices[6]*step).rgb * 2.0 - 1.0;
	normal[7] = texture(gbuffer0, texCoord + indices[7]*step).rgb * 2.0 - 1.0;
	normal[8] = texture(gbuffer0, texCoord + indices[8]*step).rgb * 2.0 - 1.0;
	
	float total_weight = 1.0;
	float discard_threshold = 0.85;

	//int i;
	// for(i = 0; i < 9; ++i) {
		// if (dot(normal[i], normal[4]) < discard_threshold) {
		// 	total_weight -= weights[i];
		// 	weights[i] = 0;
		// }
		
		if (dot(normal[0], normal[4]) < discard_threshold) {
			total_weight -= weights[0];
			weights[0] = 0;
		}
		if (dot(normal[1], normal[4]) < discard_threshold) {
			total_weight -= weights[1];
			weights[1] = 0;
		}
		if (dot(normal[2], normal[4]) < discard_threshold) {
			total_weight -= weights[2];
			weights[2] = 0;
		}
		if (dot(normal[3], normal[4]) < discard_threshold) {
			total_weight -= weights[3];
			weights[3] = 0;
		}
		if (dot(normal[4], normal[4]) < discard_threshold) {
			total_weight -= weights[4];
			weights[4] = 0;
		}
		if (dot(normal[5], normal[4]) < discard_threshold) {
			total_weight -= weights[5];
			weights[5] = 0;
		}
		if (dot(normal[6], normal[4]) < discard_threshold) {
			total_weight -= weights[6];
			weights[6] = 0;
		}
		if (dot(normal[7], normal[4]) < discard_threshold) {
			total_weight -= weights[7];
			weights[7] = 0;
		}
		if (dot(normal[8], normal[4]) < discard_threshold) {
			total_weight -= weights[8];
			weights[8] = 0;
		}
	// }
	
	float res = 0.0;
	//for (i = 0; i < 9; ++i) {	
		//res += texture(tex, texCoord + indices[i]*step).r * weights[i];
		res += texture(tex, texCoord + indices[0]*step).r * weights[0];
		res += texture(tex, texCoord + indices[1]*step).r * weights[1];
		res += texture(tex, texCoord + indices[2]*step).r * weights[2];
		res += texture(tex, texCoord + indices[3]*step).r * weights[3];
		res += texture(tex, texCoord + indices[4]*step).r * weights[4];
		res += texture(tex, texCoord + indices[5]*step).r * weights[5];
		res += texture(tex, texCoord + indices[6]*step).r * weights[6];
		res += texture(tex, texCoord + indices[7]*step).r * weights[7];
		res += texture(tex, texCoord + indices[8]*step).r * weights[8];
	//}
	res /= total_weight;
	
	gl_FragColor = vec4(res, 0.0, 0.0, 1.0);
}
