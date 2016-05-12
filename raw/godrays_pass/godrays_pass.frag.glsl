// http://http.developer.nvidia.com/GPUGems3/gpugems3_ch13.html
#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;

in vec2 texCoord;

void main() {
	const float decay = 0.96815;
	const float exposure = 0.2;
	const float density = 0.926;
	const float weight = 0.58767;
	const int NUM_SAMPLES = 10; // 100
	vec2 tc = texCoord;// * vec2(800, 600);
	vec2 lightPositionOnScreen = vec2(0.3, 0.3);
	vec2 deltaTexCoord = (tc - lightPositionOnScreen.xy);
	deltaTexCoord *= 1.0 / float(NUM_SAMPLES) * density;
	float illuminationDecay = 1.0;
	vec4 color = texture(tex, tc) * 0.4;
	// for (int i=0; i < NUM_SAMPLES; i++) {
		tc -= deltaTexCoord;
		vec4 sampleCol = texture(tex, tc) * 0.4;
		sampleCol *= illuminationDecay * weight;
		color += sampleCol;
		illuminationDecay *= decay;
		//
		tc -= deltaTexCoord;
		sampleCol = texture(tex, tc) * 0.4;
		sampleCol *= illuminationDecay * weight;
		color += sampleCol;
		illuminationDecay *= decay;
		//
		tc -= deltaTexCoord;
		sampleCol = texture(tex, tc) * 0.4;
		sampleCol *= illuminationDecay * weight;
		color += sampleCol;
		illuminationDecay *= decay;
		//
		tc -= deltaTexCoord;
		sampleCol = texture(tex, tc) * 0.4;
		sampleCol *= illuminationDecay * weight;
		color += sampleCol;
		illuminationDecay *= decay;
		//
		tc -= deltaTexCoord;
		sampleCol = texture(tex, tc) * 0.4;
		sampleCol *= illuminationDecay * weight;
		color += sampleCol;
		illuminationDecay *= decay;
		//
		tc -= deltaTexCoord;
		sampleCol = texture(tex, tc) * 0.4;
		sampleCol *= illuminationDecay * weight;
		color += sampleCol;
		illuminationDecay *= decay;
		//
		tc -= deltaTexCoord;
		sampleCol = texture(tex, tc) * 0.4;
		sampleCol *= illuminationDecay * weight;
		color += sampleCol;
		illuminationDecay *= decay;
		//
		tc -= deltaTexCoord;
		sampleCol = texture(tex, tc) * 0.4;
		sampleCol *= illuminationDecay * weight;
		color += sampleCol;
		illuminationDecay *= decay;
		//
		tc -= deltaTexCoord;
		sampleCol = texture(tex, tc) * 0.4;
		sampleCol *= illuminationDecay * weight;
		color += sampleCol;
		illuminationDecay *= decay;
		//
		tc -= deltaTexCoord;
		sampleCol = texture(tex, tc) * 0.4;
		sampleCol *= illuminationDecay * weight;
		color += sampleCol;
		illuminationDecay *= decay;
	// }
	
	gl_FragColor = color;
}
