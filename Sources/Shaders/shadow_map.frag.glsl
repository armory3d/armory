#ifdef GL_ES
precision mediump float;
#endif

varying vec4 position;

void kore() {

    float normalizedDistance = position.z / position.w;
    normalizedDistance += 0.0005;
 
    gl_FragColor = vec4(normalizedDistance, 0.0, 0.0, 1.0);
}
