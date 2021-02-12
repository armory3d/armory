#version 450

// World to view projection matrix to correctly position the vertex on screen
uniform mat4 WVP;

// Position and normal vector in local space for the current vertex
in vec3 pos;

void main() {
	gl_Position = WVP * vec4(pos, 1.0);
}
