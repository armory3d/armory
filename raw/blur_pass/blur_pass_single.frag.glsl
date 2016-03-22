#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D aomap;

in vec2 texCoord;

void main() {
	
	// float depth = (texture(aomap, texCoord).r - 0.5) * 2.0;
	
	float step = 0.002;
	
	// TOP ROW
	float s11 = (texture( aomap, texCoord + vec2( -step ) ).r);			// LEFT
	float s12 = (texture( aomap, texCoord + vec2( 0, -step ) ).r);		// MIDDLE
	float s13 = (texture( aomap, texCoord + vec2( step , -step ) ).r);	// RIGHT
 
	// MIDDLE ROW
	float s21 = (texture( aomap, texCoord + vec2( -step, 0.0 ) ).r);		// LEFT
	float col = (texture( aomap, texCoord ).r);							// DEAD CENTER
	float s23 = (texture( aomap, texCoord + vec2( -step, 0.0 ) ).r);		// RIGHT
 
	// LAST ROW
	float s31 = (texture( aomap, texCoord + vec2( -step, step ) ).r);	// LEFT
	float s32 = (texture( aomap, texCoord + vec2( 0, step ) ).r);			// MIDDLE
	float s33 = (texture( aomap, texCoord + vec2( step ) ).r);			// RIGHT
 
	// Average the color with surrounding samples
	col = (col + s11 + s12 + s13 + s21 + s23 + s31 + s32 + s33) / 9.0;
	gl_FragColor = vec4(vec3(col), 1.0);
}
