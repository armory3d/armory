#version 450

#ifdef GL_ES
precision mediump float;
#endif

#ifdef _NMTex
#define _AMTex
#endif

in vec4 position;

void main() {

    float normalizedDistance = position.z / position.w;
    normalizedDistance += 0.005;
 
    gl_FragColor = vec4(normalizedDistance, normalizedDistance, normalizedDistance, 1.0);
}
