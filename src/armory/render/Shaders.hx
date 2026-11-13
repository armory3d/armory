# Fix for Issue #2613: [$100 Bounty] Box-Project Cube Environment Mapping

// src/armory/render/Shaders.hx
class BPCEMShader extends armory.render.Shader {
    public function new() {
        super();
        this.vertexSource = "
            #ifdef GL_ES
                precision highp float;
            #endif

            attribute vec3 inPosition;
            attribute vec3 inNormal;
            attribute vec2 inTexCoord;

            uniform mat4 modelViewMatrix;
            uniform mat4 projectionMatrix;
            uniform mat4 modelMatrix;

            varying vec3 vPosition;
            varying vec3 vNormal;
            varying vec2 vTexCoord;

            void main() {
                gl_Position = projectionMatrix * modelViewMatrix * vec4(inPosition, 1.0);
                vPosition = (modelMatrix * vec4(inPosition, 1.0)).xyz;
                vNormal = (modelMatrix * vec4(inNormal, 0.0)).xyz;
                vTexCoord = inTexCoord;
            }
        ";

        this.fragmentSource = "
            #ifdef GL_ES
                precision highp float;
            #endif

            uniform samplerCube environmentMap;
            uniform float parallaxScale;

            varying vec3 vPosition;
            varying vec3 vNormal;
            varying vec2 vTexCoord;

            vec3 boxProjectedCubemap(vec3 position, vec3 normal, samplerCube environmentMap, float parallaxScale) {
                vec3 reflected = reflect(normalize(position), normal);
                vec3 boxMin = vec3(-1.0, -1.0, -1.0);
                vec3 boxMax = vec3(1.0, 1.0, 1.0);

                vec3 boxCoordinates = (reflected + 1.0) / 2.0;
                vec3 parallaxOffset = (boxCoordinates - 0.5) * parallaxScale;

                vec3 finalPosition = position + parallaxOffset;
                vec3 finalNormal = normal;

                return textureCube(environmentMap, finalPosition).rgb;
            }

            void main() {
                gl_FragColor = vec4(boxProjectedCubemap(vPosition, vNormal, environmentMap, parallaxScale), 1.0);
            }
        ";
    }
}

// src/armory/render/EnvironmentMap.hx
class EnvironmentMap {
    public var texture:Texture;
    public var parallaxScale:Float;

    public function new(texture:Texture, parallaxScale:Float) {
        this.texture = texture;
        this.parallaxScale = parallaxScale;
    }
}

// src/armory/scene/Object.hx
class Object {
    public var environmentMap:EnvironmentMap;

    public function new() {
        this.environmentMap = null;
    }

    public function setEnvironmentMap(environmentMap:EnvironmentMap) {
        this.environmentMap = environmentMap;
    }
}