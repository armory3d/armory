# Fix for Issue #2611: [$100 Bounty] Stochastic Screen-Space Reflections

# armory/core/shaders/postprocess.glsl
# ...
uniform sampler2D u_SSRTexture;
uniform float u_SSRQuality;
uniform bool u_UseStochasticSSR;

# ...
void main() {
    # ...
    if (u_UseStochasticSSR) {
        vec3 ssrColor = stochasticSSR(u_SSRTexture, u_SSRQuality);
        gl_FragColor = mix(gl_FragColor, vec4(ssrColor, 1.0), u_SSRQuality);
    }
    # ...
}

# armory/core/shaders/ssr.glsl
# ...
float hash(vec2 n) {
    return fract(sin(dot(n, vec2(12.9898, 4.1414))) * 43758.5453);
}

vec3 stochasticSSR(sampler2D texture, float quality) {
    vec2 texelSize = 1.0 / textureSize(texture, 0);
    vec2 uv = gl_FragCoord.xy * texelSize;
    vec3 color = vec3(0.0);
    float totalWeight = 0.0;
    
    for (int i = 0; i < 16; i++) {
        vec2 offset = vec2(hash(vec2(i, uv.x)), hash(vec2(i, uv.y))) * 2.0 - 1.0;
        offset *= texelSize * quality;
        vec2 sampleUV = uv + offset;
        vec4 sampleColor = texture2D(texture, sampleUV);
        float weight = sampleColor.a;
        color += sampleColor.rgb * weight;
        totalWeight += weight;
    }
    
    return color / totalWeight;
}

# armory/ui/postprocess.hx
# ...
class PostProcess {
    # ...
    public var useStochasticSSR:Bool = false;
    public var ssrQuality:Float = 1.0;
    # ...
}

# armory/ui/postprocess.hxml
# ...
<window>
    # ...
    <checkbox label="Use Stochastic SSR" var="postprocess.useStochasticSSR" />
    <slider label="SSR Quality" var="postprocess.ssrQuality" min="0.1" max="2.0" step="0.1" />
    # ...
</window>