#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D aomap;
uniform sampler2D gmap;
uniform vec2 dir;

in vec2 texCoord;

vec3 normalFromDepth(float depth, vec2 texcoords) {
	const vec2 offset1 = vec2(0.0, 0.001);
	const vec2 offset2 = vec2(0.001, 0.0);

	float depth1 = (texture(gmap, texcoords + offset1).r - 0.5) * 2.0;
	float depth2 = (texture(gmap, texcoords + offset2).r - 0.5) * 2.0;

	vec3 p1 = vec3(offset1, depth1 - depth);
	vec3 p2 = vec3(offset2, depth2 - depth);

	vec3 normal = cross(p1, p2);
	normal.z = -normal.z;

	return normalize(normal);
}

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

	vec2 step = dir / vec2(1136.0, 640.0); //g_resolution.xy;
	
	vec3 normal[9];

	float depth = (texture(gmap, texCoord + indices[0]*step).r - 0.5) * 2.0;
	normal[0] = normalFromDepth(depth, texCoord);
	
	depth = (texture(gmap, texCoord + indices[1]*step).r - 0.5) * 2.0;
	normal[1] = normalFromDepth(depth, texCoord);
	
	depth = (texture(gmap, texCoord + indices[2]*step).r - 0.5) * 2.0;
	normal[2] = normalFromDepth(depth, texCoord);
	
	depth = (texture(gmap, texCoord + indices[3]*step).r - 0.5) * 2.0;
	normal[3] = normalFromDepth(depth, texCoord);
	
	depth = (texture(gmap, texCoord + indices[4]*step).r - 0.5) * 2.0;
	normal[4] = normalFromDepth(depth, texCoord);
	
	depth = (texture(gmap, texCoord + indices[5]*step).r - 0.5) * 2.0;
	normal[5] = normalFromDepth(depth, texCoord);
	
	depth = (texture(gmap, texCoord + indices[6]*step).r - 0.5) * 2.0;
	normal[6] = normalFromDepth(depth, texCoord);
	
	depth = (texture(gmap, texCoord + indices[7]*step).r - 0.5) * 2.0;
	normal[7] = normalFromDepth(depth, texCoord);
	
	depth = (texture(gmap, texCoord + indices[8]*step).r - 0.5) * 2.0;
	normal[8] = normalFromDepth(depth, texCoord);
	
	// normal[0] = texture(gmap, texCoord + indices[0]*step).r;
	// normal[1] = texture(gmap, texCoord + indices[1]*step).r;
	// normal[2] = texture(gmap, texCoord + indices[2]*step).r;
	// normal[3] = texture(gmap, texCoord + indices[3]*step).r;
	// normal[4] = texture(gmap, texCoord + indices[4]*step).r;
	// normal[5] = texture(gmap, texCoord + indices[5]*step).r;
	// normal[6] = texture(gmap, texCoord + indices[6]*step).r;
	// normal[7] = texture(gmap, texCoord + indices[7]*step).r;
	// normal[8] = texture(gmap, texCoord + indices[8]*step).r;
	
	float total_weight = 1.0;
	float discard_threshold = 0.85;

	int i;
	for(i = 0; i < 9; ++i) {
		if (dot(normal[i], normal[4]) < discard_threshold) {
			total_weight -= weights[i];
			weights[i] = 0;
		}
	}
	
	float res = 0.0;
	for (i = 0; i < 9; ++i) {	
		res += texture(aomap, texCoord + indices[i]*step).r * weights[i];
	}
	res /= total_weight;
	
	gl_FragColor = vec4(vec3(res), 1.0);
}
