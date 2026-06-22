#version 330

in vec3 pos;
out vec2 texCoord;
in vec2 tex;

void main()
{
    gl_Position = vec4(pos.x, pos.y, 0.5, 1.0);
    texCoord = tex;
}

