//
// Copyright (C) 2012 Jorge Jimenez (jorge@iryoku.com)
// Copyright (C) 2012 Diego Gutierrez (diegog@unizar.es)
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
// 
//    1. Redistributions of source code must retain the above copyright notice,
//       this list of conditions and the following disclaimer.
//
//    2. Redistributions in binary form must reproduce the following disclaimer
//       in the documentation and/or other materials provided with the 
//       distribution:
//
//       "Uses Separable SSS. Copyright (C) 2012 by Jorge Jimenez and Diego
//        Gutierrez."
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS 
// IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
// THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
// PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL COPYRIGHT HOLDERS OR CONTRIBUTORS 
// BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
// POSSIBILITY OF SUCH DAMAGE.
//
// The views and conclusions contained in the software and documentation are 
// those of the authors and should not be interpreted as representing official
// policies, either expressed or implied, of the copyright holders.
//

#version 450

#include "compiled.inc"

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D tex;

uniform vec2 dir;
uniform vec2 cameraProj;

in vec2 texCoord;
out vec4 fragColor;

const float SSSS_FOVY = 45.0;

// Separable SSS Reflectance
// const float sssWidth = 0.005;
vec4 SSSSBlur() {
	// Quality = 0
	const int SSSS_N_SAMPLES  = 11;
	vec4 kernel[SSSS_N_SAMPLES];		
	kernel[0] = vec4(0.560479, 0.669086, 0.784728, 0);
	kernel[1] = vec4(0.00471691, 0.000184771, 5.07566e-005, -2);
	kernel[2] = vec4(0.0192831, 0.00282018, 0.00084214, -1.28);
	kernel[3] = vec4(0.03639, 0.0130999, 0.00643685, -0.72);
	kernel[4] = vec4(0.0821904, 0.0358608, 0.0209261, -0.32);
	kernel[5] = vec4(0.0771802, 0.113491, 0.0793803, -0.08);
	kernel[6] = vec4(0.0771802, 0.113491, 0.0793803, 0.08);
	kernel[7] = vec4(0.0821904, 0.0358608, 0.0209261, 0.32);
	kernel[8] = vec4(0.03639, 0.0130999, 0.00643685, 0.72);
	kernel[9] = vec4(0.0192831, 0.00282018, 0.00084214, 1.28);
	kernel[10] = vec4(0.00471691, 0.000184771, 5.07565e-005, 2);
	
	vec4 colorM = textureLod(tex, texCoord, 0.0);

	// Fetch linear depth of current pixel
	float depth = textureLod(gbufferD, texCoord, 0.0).r;
	float depthM = cameraProj.y / (depth - cameraProj.x);

	// Calculate the sssWidth scale (1.0 for a unit plane sitting on the projection window)
	float distanceToProjectionWindow = 1.0 / tan(0.5 * radians(SSSS_FOVY));
	float scale = distanceToProjectionWindow / depthM;

	// Calculate the final step to fetch the surrounding pixels
	vec2 finalStep = sssWidth * scale * dir;
	// finalStep *= 1.0;//SSSS_STREGTH_SOURCE; // Modulate it using the alpha channel.
	finalStep *= 1.0 / 3.0; // Divide by 3 as the kernels range from -3 to 3.
	
	finalStep *= 0.05; //

	// Accumulate the center sample:
	vec4 colorBlurred = colorM;
	colorBlurred.rgb *= kernel[0].rgb;

	// Accumulate the other samples
	for (int i = 1; i < SSSS_N_SAMPLES; i++) {
		// Fetch color and depth for current sample
		vec2 offset = texCoord + kernel[i].a * finalStep;
		vec4 color = textureLod(tex, offset, 0.0);
		// #if SSSS_FOLLOW_SURFACE == 1
		// If the difference in depth is huge, we lerp color back to "colorM":
		// float depth = textureLod(depthTex, offset, 0.0).r;
		// float s = SSSSSaturate(300.0f * distanceToProjectionWindow *
							//    sssWidth * abs(depthM - depth));
		// color.rgb = SSSSLerp(color.rgb, colorM.rgb, s);
		// #endif
		// Accumulate
		colorBlurred.rgb += kernel[i].rgb * color.rgb;
	}

	return colorBlurred;
}

void main() {
	// SSS only masked objects
	if (textureLod(gbuffer0, texCoord, 0.0).a == 2.0) {
		fragColor = clamp(SSSSBlur(), 0.0, 1.0);
	}
	else {
		fragColor = textureLod(tex, texCoord, 0.0);
	}
}
