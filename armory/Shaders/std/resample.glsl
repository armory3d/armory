#ifndef _RESAMPLE_GLSL_
#define _RESAMPLE_GLSL_

float karisWeight(const vec3 value) {
	// Using brightness instead of luma
	return 1.0 / (1.0 + max(value.r, max(value.g, value.b)));
}

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

vec3 downsample_box_filter_anti_flicker(const sampler2D tex, const vec2 texCoord, const vec2 texelSize) {
	vec4 delta = texelSize.xyxy * vec4(-0.5, -0.5, 0.5, 0.5);

	vec3 bl = textureLod(tex, texCoord + delta.xy, 0.0).rgb;
	vec3 br = textureLod(tex, texCoord + delta.zy, 0.0).rgb;
	vec3 tl = textureLod(tex, texCoord + delta.xw, 0.0).rgb;
	vec3 tr = textureLod(tex, texCoord + delta.zw, 0.0).rgb;

	// Weighted averaging technique by Brian Karis to reduce fireflies:
	// http://graphicrants.blogspot.com/2013/12/tone-mapping.html
	float blWeight = karisWeight(bl);
	float brWeight = karisWeight(br);
	float tlWeight = karisWeight(tl);
	float trWeight = karisWeight(tr);

	return (bl * blWeight + br * brWeight + tl * tlWeight + tr * trWeight) / (blWeight + brWeight + tlWeight + trWeight);
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

vec3 downsample_dual_filter_anti_flicker(const sampler2D tex, const vec2 texCoord, const vec2 texelSize) {
	vec3 delta = texelSize.xyx * vec3(0.5, 0.5, -0.5);

	vec3 c  = textureLod(tex, texCoord,            0.0).rgb;
	vec3 bl = textureLod(tex, texCoord - delta.xy, 0.0).rgb;
	vec3 br = textureLod(tex, texCoord - delta.zy, 0.0).rgb;
	vec3 tl = textureLod(tex, texCoord + delta.zy, 0.0).rgb;
	vec3 tr = textureLod(tex, texCoord + delta.xy, 0.0).rgb;

	float cWeight  = karisWeight(c) * 4.0;
	float blWeight = karisWeight(bl);
	float brWeight = karisWeight(br);
	float tlWeight = karisWeight(tl);
	float trWeight = karisWeight(tr);

	return (c * cWeight + bl * blWeight + br * brWeight + tl * tlWeight + tr * trWeight) / (cWeight + blWeight + brWeight + tlWeight + trWeight);
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

vec3 downsample_13_tap_anti_flicker(const sampler2D tex, const vec2 texCoord, const vec2 texelSize) {
	vec4 delta = texelSize.xyxy * vec4(1.0, 1.0, -1.0, 0.0);
	vec4 deltaHalf = delta * 0.5;

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

	// Apply Karis average to groups of four sampled values, adapted from
	// Jimenez 2014. The similar but faster implementation from
	// https://learnopengl.com/Guest-Articles/2022/Phys.-Based-Bloom
	// doesn't work as it doesn't really reduce fireflies :/

	float TLWeight = karisWeight(TL);
	float TWeight  = karisWeight(T);
	float TRWeight = karisWeight(TR);

	float LWeight  = karisWeight(L);
	float CWeight  = karisWeight(C);
	float RWeight  = karisWeight(R);

	float BLWeight = karisWeight(BL);
	float BWeight  = karisWeight(B);
	float BRWeight = karisWeight(BR);

	float tlWeight = karisWeight(tl);
	float trWeight = karisWeight(tr);
	float blWeight = karisWeight(bl);
	float brWeight = karisWeight(br);

	vec3 result;
	result  = 0.125 * (TL * TLWeight + T * TWeight + L * LWeight + C * CWeight) / (TLWeight + TWeight + LWeight + CWeight);
	result += 0.125 * (T * TWeight + TR * TRWeight + C * CWeight + R * RWeight) / (TWeight + TRWeight + CWeight + RWeight);
	result += 0.125 * (L * LWeight + C * CWeight + BL * BLWeight + B * BWeight) / (LWeight + CWeight + BLWeight + BWeight);
	result += 0.125 * (C * CWeight + R * RWeight + B * BWeight + R * RWeight) / (CWeight + RWeight + BWeight + RWeight);
	result += 0.5   * (tl * tlWeight + tr * trWeight + bl * blWeight + br * brWeight) / (tlWeight + trWeight + blWeight + brWeight);

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
