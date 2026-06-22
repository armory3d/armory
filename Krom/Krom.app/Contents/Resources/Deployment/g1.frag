#version 330

uniform sampler2D texy;

out vec4 FragColor;
in vec2 texCoord;

void main()
{
    FragColor = texture(texy, texCoord);
}

