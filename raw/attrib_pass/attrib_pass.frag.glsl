#version 450

#extension GL_EXT_draw_buffers : require

#ifdef GL_ES
precision mediump float;
#endif

#ifdef _NormalMapping
#define _Texturing
#endif


#ifdef _Texturing
uniform sampler2D stex;
#endif
uniform sampler2D shadowMap;
#ifdef _NormalMapping
uniform sampler2D normalMap;
#endif
uniform bool lighting;
uniform bool receiveShadow;
uniform float roughness;

in vec3 position;
#ifdef _Texturing
in vec2 texCoord;
#endif
in vec3 normal;
in vec4 lPos;
in vec4 matColor;
in vec3 lightDir;
in vec3 eyeDir;

void main() {

	gl_FragData[0] = vec4(position.xyz, 0);
	gl_FragData[1] = vec4(normal.xyz, 0);
	#ifdef _Texturing
	gl_FragData[2] = vec4(texture(stex, texCoord).rgb, 0);
	#endif
}
