#version 450

#ifdef GL_ES
precision highp float;
#endif

uniform sampler2D tex;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
uniform sampler2D gbuffer2;
const float focus_depth = 0.5;
in vec2 texCoord;

const float vignout = 1.3; // vignetting outer border
const float vignin = 0.0; // vignetting inner border
const float vignfade = 90.0; // f-stops till vignete fades
const float fstop = 20; // f-stop value

float vignette() {
	float dist = distance(texCoord, vec2(0.5,0.5));
	dist = smoothstep(vignout + (fstop / vignfade), vignin + (fstop / vignfade), dist);
	return clamp(dist, 0.0, 1.0);
}

vec4 sampleBox(float size) {
	vec4 color = vec4(0.0, 0.0, 0.0, 0.0);
	color += texture(tex, vec2(texCoord.x - size, texCoord.y - size)) * 0.075;
	color += texture(tex, vec2(texCoord.x, texCoord.y - size)) * 0.1;
	color += texture(tex, vec2(texCoord.x + size, texCoord.y - size)) * 0.075;
	color += texture(tex, vec2(texCoord.x - size, texCoord.y)) * 0.1;
	color += texture(tex, vec2(texCoord.x, texCoord.y)) * 0.30;
	color += texture(tex, vec2(texCoord.x + size, texCoord.y)) * 0.1;
	color += texture(tex, vec2(texCoord.x - size, texCoord.y + size)) * 0.075;
	color += texture(tex, vec2(texCoord.x, texCoord.y + size)) * 0.1;
	color += texture(tex, vec2(texCoord.x + size, texCoord.y + size)) * 0.075;
	return color;
}

void main() {
	float depth = texture(gbuffer0, texCoord).a;
	float blur_amount = abs(depth - focus_depth);
	if(depth < depth - focus_depth) {
		blur_amount *= 10.0;
	}
	blur_amount = clamp(blur_amount, 0.0, 1.0);
	vec4 baseColor = texture(tex, texCoord);
	vec4 blurredColor = vec4(0.0, 0.0, 0.0, 0.0);
	float blurSize = 0.005 * blur_amount;
	blurredColor = 0.75 * sampleBox(blurSize * 0.5) + 0.25 * sampleBox(blurSize * 1.0);
	vec4 col = baseColor * (1.0 - blur_amount) + blurredColor * blur_amount;
	
	// Vignetting
	col *= vignette();
	
	gl_FragColor = col; 
}
