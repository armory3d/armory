#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;

in vec2 texCoord;


// Temporal Resolve Pixel Shader (Optional Pass)

vec4 SMAAResolvePS(vec2 texcoord, sampler2D currentColorTex, sampler2D previousColorTex
                     //#if SMAA_REPROJECTION
                     //, sampler2D velocityTex
                     //#endif
                     ) {
    // #if SMAA_REPROJECTION
    // // Velocity is assumed to be calculated for motion blur, so we need to
    // // inverse it for reprojection:
    // vec2 velocity = -SMAA_DECODE_VELOCITY(texture(velocityTex, texcoord).rg);

    // // Fetch current pixel:
    // vec4 current = texture(currentColorTex, texcoord);

    // // Reproject current coordinates and fetch previous pixel:
    // vec4 previous = texture(previousColorTex, texcoord + velocity);

    // // Attenuate the previous pixel if the velocity is different:
    // float delta = abs(current.a * current.a - previous.a * previous.a) / 5.0;
    // float weight = 0.5 * saturate(1.0 - sqrt(delta) * SMAA_REPROJECTION_WEIGHT_SCALE);

    // // Blend the pixels according to the calculated weight:
    // return lerp(current, previous, weight);
    // #else
    // Just blend the pixels:
    vec4 current = texture(currentColorTex, texcoord);
    vec4 previous = texture(previousColorTex, texcoord);
    return lerp(current, previous, 0.5);
    // #endif
}


void main() {
    // gl_FragColor = vec4(col);
}
