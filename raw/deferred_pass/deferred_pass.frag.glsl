#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D gbuffer0; // Positions
uniform sampler2D gbuffer1; // Normals
uniform sampler2D gbuffer2; // Textures

varying vec2 texCoord;

void main() {

	gl_FragColor = vec4(texture2D(gbuffer2, texCoord).rgb, 1.0);
}
