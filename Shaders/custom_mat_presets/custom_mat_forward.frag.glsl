#version 450

// World-space normal from the vertex shader stage
in vec3 wnormal;

// Color of each fragment on the screen
out vec4 fragColor;

void main() {
    // Shadeless white color
    fragColor = vec4(1.0);
}
