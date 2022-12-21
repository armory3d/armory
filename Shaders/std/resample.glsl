#ifndef _RESAMPLE_GLSL_
#define _RESAMPLE_GLSL_

/**
	Downsampling using a 4x4 box filter.
**/
vec3 downsample_box_filter(const sampler2D tex, const vec2 texCoord, const vec2 texelSize) {
	vec4 delta = texelSize.xyxy * vec4(-0.5, -0.5, 0.5, 0.5);

	vec3 result;
	result  = textureLod(tex, texCoord + delta.xy, 0.0).rgb;
	result += textureLod(tex, texCoord + delta.zy, 0.0).rgb;
	result += textureLod(tex, texCoord + delta.xw, 0.0).rgb;
	result += textureLod(tex, texCoord + delta.zw, 0.0).rgb;

	return result * (1.0 / 4.0);
}

/**
	Downsample using the "dual filtering" technique from "Bandwidth-Efficient Rendering"
	by Marius Bjørge, Siggraph 2015:
	https://community.arm.com/cfs-file/__key/communityserver-blogs-components-weblogfiles/00-00-00-20-66/siggraph2015_2D00_mmg_2D00_marius_2D00_slides.pdf
**/
vec3 downsample_dual_filter(const sampler2D tex, const vec2 texCoord, const vec2 texelSize) {
	vec3 delta = texelSize.xyx * vec3(0.5, 0.5, -0.5);

	vec3 result;
	result  = textureLod(tex, texCoord,            0.0).rgb * 4.0;
	result += textureLod(tex, texCoord - delta.xy, 0.0).rgb;
	result += textureLod(tex, texCoord - delta.zy, 0.0).rgb;
	result += textureLod(tex, texCoord + delta.zy, 0.0).rgb;
	result += textureLod(tex, texCoord + delta.xy, 0.0).rgb;

	return result * (1.0 / 8.0);
}

/**
	Downsample using the approach from "NEXT GENERATION POST PROCESSING IN CALL OF DUTY: ADVANCED WARFARE"
	by Jorge Jimenez, SIGGRAPH 2014: https://advances.realtimerendering.com/s2014/#_NEXT_GENERATION_POST
**/
vec3 downsample_13_tap(const sampler2D tex, const vec2 texCoord, const vec2 texelSize) {
	/*
		| TL   T   TR |
		|   tl   tr   |
		| L    C    R |
		|   bl   br   |
		| BL   B   BR |
	*/

	vec4 delta = texelSize.xyxy * vec4(1.0, 1.0, -1.0, 0.0);
	vec4 deltaHalf = delta * 0.5;

	// TODO investigate if sampling in morton order is faster here

	vec3 TL = textureLod(tex, texCoord + delta.zy, 0.0).rgb;
	vec3 T  = textureLod(tex, texCoord + delta.wy, 0.0).rgb;
	vec3 TR = textureLod(tex, texCoord + delta.xy, 0.0).rgb;

	vec3 L  = textureLod(tex, texCoord + delta.zw, 0.0).rgb;
	vec3 C  = textureLod(tex, texCoord,            0.0).rgb;
	vec3 R  = textureLod(tex, texCoord + delta.xw, 0.0).rgb;

	vec3 BL = textureLod(tex, texCoord - delta.xy, 0.0).rgb;
	vec3 B  = textureLod(tex, texCoord - delta.wy, 0.0).rgb;
	vec3 BR = textureLod(tex, texCoord - delta.zy, 0.0).rgb;

	vec3 tl = textureLod(tex, texCoord + deltaHalf.zy, 0.0).rgb;
	vec3 tr = textureLod(tex, texCoord + deltaHalf.xy, 0.0).rgb;
	vec3 bl = textureLod(tex, texCoord - deltaHalf.xy, 0.0).rgb;
	vec3 br = textureLod(tex, texCoord - deltaHalf.zy, 0.0).rgb;

	vec3 result;
	result = C * 0.125;
	result += (TL + TR + BL + BR) * 0.03125;
	result += (T + L + R + B) * 0.0625;
	result += (tl + tr + bl + br) * 0.125;
	return result;
}

vec3 upsample_4tap_bilinear(const sampler2D tex, const vec2 texCoord, const vec2 texelSize, const float sampleScale) {
	vec3 delta = texelSize.xyx * vec3(1.0, 1.0, -1.0) * sampleScale;

	vec3 result;
	result  = textureLod(tex, texCoord - delta.xy, 0.0).rgb;
	result += textureLod(tex, texCoord - delta.zy, 0.0).rgb;
	result += textureLod(tex, texCoord + delta.zy, 0.0).rgb;
	result += textureLod(tex, texCoord + delta.xy, 0.0).rgb;

	return result * (1.0 / 4.0);
}

vec3 upsample_dual_filter(const sampler2D tex, const vec2 texCoord, const vec2 texelSize, const float sampleScale) {
	vec2 delta = texelSize * sampleScale;

	vec3 result;
	result  = textureLod(tex, texCoord + vec2(-delta.x * 2.0, 0.0), 0.0).rgb;
	result += textureLod(tex, texCoord + vec2(-delta.x, delta.y),   0.0).rgb * 2.0;
	result += textureLod(tex, texCoord + vec2(0.0, delta.y * 2.0),  0.0).rgb;
	result += textureLod(tex, texCoord + delta,                     0.0).rgb * 2.0;
	result += textureLod(tex, texCoord + vec2(delta.x * 2.0, 0.0),  0.0).rgb;
	result += textureLod(tex, texCoord + vec2(delta.x, -delta.y),   0.0).rgb * 2.0;
	result += textureLod(tex, texCoord + vec2(0.0, -delta.y * 2.0), 0.0).rgb;
	result += textureLod(tex, texCoord - delta,                     0.0).rgb * 2.0;

	return result * (1.0 / 12.0);
}

/**
	3x3 (9-tap) tent/bartlett filter, which approximates gaussian blur if applied repeatedly:
	- Wojciech Jarosz: Fast Image Convolutions
		http://elynxsdk.free.fr/ext-docs/Blur/Fast_box_blur.pdf
	- Martin Kraus, Magnus Strengert: Pyramid Filters Based on Bilinear Interpolation
		https://www.cs.cit.tum.de/fileadmin/w00cfj/cg/Research/Publications/2007/Pyramid_Filters/GRAPP07.pdf
**/
vec3 upsample_tent_filter_3x3(const sampler2D tex, const vec2 texCoord, const vec2 texelSize, const float sampleScale) {
	vec4 delta = texelSize.xyxy * vec4(1.0, 1.0, -1.0, 0.0) * sampleScale;

	vec3 result;
	result  = textureLod(tex, texCoord - delta.xy, 0.0).rgb;
	result += textureLod(tex, texCoord - delta.wy, 0.0).rgb * 2.0;
	result += textureLod(tex, texCoord - delta.zy, 0.0).rgb;

	result += textureLod(tex, texCoord + delta.zw, 0.0).rgb * 2.0;
	result += textureLod(tex, texCoord           , 0.0).rgb * 4.0;
	result += textureLod(tex, texCoord + delta.xw, 0.0).rgb * 2.0;

	result += textureLod(tex, texCoord + delta.zy, 0.0).rgb;
	result += textureLod(tex, texCoord + delta.wy, 0.0).rgb * 2.0;
	result += textureLod(tex, texCoord + delta.xy, 0.0).rgb;

	return result * (1.0 / 16.0);
}

#endif
