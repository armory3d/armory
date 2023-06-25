#version 450

#include "compiled.inc"

uniform sampler2D tex;

#ifdef _CPostprocess
uniform vec3 PPComp13;
#endif

in vec2 texCoord;
out vec4 fragColor;

vec2 barrelDistortion(vec2 coord, float amt) {
	vec2 cc = coord - 0.5;
	float dist = dot(cc, cc);
	return coord + cc * dist * amt;
}
float sat(float value)
{
	return clamp(value, 0.0, 1.0);
}
float linterp(float t) {
	return sat(1.0 - abs(2.0 * t - 1.0) );
}
float remap(float t, float a, float b ) {
	return sat((t - a) / (b - a));
}
vec4 spectrum_offset(float t) {
	vec4 ret;
	float low = step(t,0.5);
	float high = 1.0 - low;
	float minMap = 1.0;
	float maxMap = 6.0;
	float w = linterp( remap(t, minMap/maxMap, 5.0/maxMap ) );
	ret = vec4(low, 1.0, high, 1.) * vec4(1.0-w, w, 1.0-w, 1.0);

	return pow(ret, vec4(1.0/2.2) );
}

void main() {

	#ifdef _CPostprocess
		float max_distort = PPComp13.x;
		int num_iter = int(PPComp13.y);
	#else
		float max_distort = compoChromaticStrength;
		int num_iter = compoChromaticSamples;
	#endif

	// Spectral
	if (compoChromaticType == 1) {
		float reci_num_iter_f = 1.0 / float(num_iter);

		vec2 resolution = vec2(1,1);
		vec2 uv = (texCoord.xy/resolution.xy);
		vec4 sumcol = vec4(0.0);
		vec4 sumw = vec4(0.0);
		for (int i=0; i < num_iter; ++i)
		{
			float t = float(i) * reci_num_iter_f;
			vec4 w = spectrum_offset(t);
			sumw += w;
			sumcol += w * texture(tex, barrelDistortion(uv, 0.6 * max_distort * t));
		}

		fragColor = sumcol / sumw;
	}

	// Simple
	else {
		vec3 col = vec3(0.0);
		col.x = texture(tex, texCoord + ((vec2(0.0, 1.0) * max_distort) / vec2(1000.0))).x;
		col.y = texture(tex, texCoord + ((vec2(-0.85, -0.5) * max_distort) / vec2(1000.0))).y;
		col.z = texture(tex, texCoord + ((vec2(0.85, -0.5) * max_distort) / vec2(1000.0))).z;
		fragColor = vec4(col.x, col.y, col.z, fragColor.w);
	}
}
