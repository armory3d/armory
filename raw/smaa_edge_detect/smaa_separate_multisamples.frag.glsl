#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;

in vec2 texCoord;


// Separate Multisamples Pixel Shader (Optional Pass)

#ifdef SMAALoad
void SMAASeparatePS(vec4 position,
                    vec2 texcoord,
                    out vec4 target0,
                    out vec4 target1,
                    SMAATexture2DMS2(colorTexMS)) {
    ivec2 pos = ivec2(position.xy);
    target0 = SMAALoad(colorTexMS, pos, 0);
    target1 = SMAALoad(colorTexMS, pos, 1);
}
#endif


void main() {
    // gl_FragColor = vec4(col);
}
