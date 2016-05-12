#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;
// uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform vec2 dir;

in vec2 texCoord;

void main() {
	
	vec2 pixelStep = dir / vec2(800, 600);
	vec3 blurredResult = vec3( 0.0, 0.0, 0.0 );
	
	float depth = texture(gbuffer0, texCoord).a;
	float weight = 0.0;
	
	// for (float i = -3.0; i <= 3.0; i += 1.0) {
		// float pixelDepth = texture(gbuffer0, texCoord + i * pixelStep).a;
		// float pixelWeight = max(0.0, 1.0 - step(0.2, abs(depth - pixelDepth)));
		// weight += pixelWeight;
		// blurredResult += texture(tex, texCoord + i * pixelStep).rgb * pixelWeight;
		
		float pixelDepth = texture(gbuffer0, texCoord + pixelStep * -3).a;
		float pixelWeight = max(0.0, 1.0 - step(0.2, abs(depth - pixelDepth)));
		weight += pixelWeight;
		blurredResult += texture(tex, texCoord + pixelStep * -3).rgb * pixelWeight;
		
		pixelDepth = texture(gbuffer0, texCoord + pixelStep * -2).a;
		pixelWeight = max(0.0, 1.0 - step(0.2, abs(depth - pixelDepth)));
		weight += pixelWeight;
		blurredResult += texture(tex, texCoord + pixelStep * -2).rgb * pixelWeight;
		
		pixelDepth = texture(gbuffer0, texCoord + pixelStep * -1).a;
		pixelWeight = max(0.0, 1.0 - step(0.2, abs(depth - pixelDepth)));
		weight += pixelWeight;
		blurredResult += texture(tex, texCoord + pixelStep * -1).rgb * pixelWeight;
		
		pixelDepth = texture(gbuffer0, texCoord + pixelStep * 0).a;
		pixelWeight = max(0.0, 1.0 - step(0.2, abs(depth - pixelDepth)));
		weight += pixelWeight;
		blurredResult += texture(tex, texCoord + pixelStep * 0).rgb * pixelWeight;
		
		pixelDepth = texture(gbuffer0, texCoord + pixelStep * 1).a;
		pixelWeight = max(0.0, 1.0 - step(0.2, abs(depth - pixelDepth)));
		weight += pixelWeight;
		blurredResult += texture(tex, texCoord + pixelStep * 1).rgb * pixelWeight;
		
		pixelDepth = texture(gbuffer0, texCoord + pixelStep * 2).a;
		pixelWeight = max(0.0, 1.0 - step(0.2, abs(depth - pixelDepth)));
		weight += pixelWeight;
		blurredResult += texture(tex, texCoord + pixelStep * 2).rgb * pixelWeight;
		
		pixelDepth = texture(gbuffer0, texCoord + pixelStep * 3).a;
		pixelWeight = max(0.0, 1.0 - step(0.2, abs(depth - pixelDepth)));
		weight += pixelWeight;
		blurredResult += texture(tex, texCoord + pixelStep * 3).rgb * pixelWeight;
	// }
	
	blurredResult /= weight;
	gl_FragColor = vec4(vec3(blurredResult), 1.0);
}
