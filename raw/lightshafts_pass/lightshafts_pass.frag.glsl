// http://http.developer.nvidia.com/GPUGems3/gpugems3_ch13.html
// http://developer.download.nvidia.com/SDK/10.5/direct3d/samples.html#VolumeLight
#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;
uniform sampler2D gbufferD;

in vec2 texCoord;
out vec4 outColor;

void main() {
	const float decay = 0.96815;
	const float exposure = 0.2;
	const float density = 0.926;
	const float weight = 0.58767;
	const int NUM_SAMPLES = 40;
	vec2 tc = texCoord;
	vec2 lightScreenSpace = vec2(0.3, 0.3);
	vec2 deltaTexCoord = (tc - lightScreenSpace.xy);
	deltaTexCoord *= 1.0 / float(NUM_SAMPLES) * density;
	float illuminationDecay = 1.0;
	vec4 color = texture(tex, tc) * 0.4;
	for (int i = 0; i < NUM_SAMPLES; i++) {
		tc -= deltaTexCoord;
		if (texture(gbufferD, tc).r > 0.99) color += texture(tex, tc) * 0.4;
		color *= illuminationDecay * weight;
		illuminationDecay *= decay;
	}
	outColor = color;
}
