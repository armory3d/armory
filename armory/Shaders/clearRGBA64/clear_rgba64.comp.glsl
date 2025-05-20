#version 450

layout(rgba16) uniform image3D image;

layout(local_size_x = 8, local_size_y = 8, local_size_z = 8) in;

void main() {
    ivec3 coord = ivec3(gl_GlobalInvocationID.xyz);
    imageStore(image, coord, vec4(0.0));
}
