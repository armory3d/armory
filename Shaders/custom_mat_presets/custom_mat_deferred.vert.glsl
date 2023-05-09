#version 450

// World to view projection matrix to correctly position the vertex on screen
uniform mat4 WVP;
// Matrix to transform normals from local into world space
uniform mat3 N;

// Position and normal vectors of the current vertex in local space
// Armory packs the vertex data to preserve memory, so nor.z values are
// saved in pos.w
in vec4 pos; // pos.xyz, nor.w
in vec2 nor; // nor.xy

// Normal vector in world space
out vec3 wnormal;

void main() {
	wnormal = normalize(N * vec3(nor.xy, pos.w));
	gl_Position = WVP * vec4(pos.xyz, 1.0);
}
