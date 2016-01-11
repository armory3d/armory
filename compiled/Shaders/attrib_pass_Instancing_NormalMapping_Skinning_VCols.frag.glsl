#define _Instancing
#define _NormalMapping
#define _Skinning
#define _VCols
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

varying vec3 position;
#ifdef _Texturing
varying vec2 texCoord;
#endif
varying vec3 normal;
varying vec4 lPos;
varying vec4 matColor;
varying vec3 lightDir;
varying vec3 eyeDir;

void kore() {

	gl_FragData[0] = vec4(position.xyz, 0);
	gl_FragData[1] = vec4(normal.xyz, 0);
	#ifdef _Texturing
	gl_FragData[2] = vec4(texture2D(stex, texCoord).rgb, 0);
	#endif
}
