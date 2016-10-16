#version 450

in vec3 pos;
// in vec3 nor;
#ifdef _Tex
	in vec2 tex;
#endif
#ifdef _VCols
	in vec3 col;
#endif
#ifdef _NorTex
	in vec3 tan;
#endif
#ifdef _Skinning
	in vec4 bone;
	in vec4 weight;
#endif
#ifdef _Instancing
	in vec3 off;
#endif

uniform mat4 LWVP;
uniform mat4 W;

out vertData {
#ifdef _BaseTex
    vec2 texuv;
#endif
    vec4 lampPos;
} vert;

void main() {
#ifdef _Tex
    vert.texuv = tex;
#endif
    vert.lampPos = LWVP * vec4(pos, 1.0);
    gl_Position = W * vec4(pos, 1.0);
}
