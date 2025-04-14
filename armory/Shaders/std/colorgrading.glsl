// Colorgrading library functions - Inspired by UE4
//No specific license (maybe zlib), but just do whatever

#define LUMINANCE_PRESERVATION 0.75
#define EPSILON 1e-10
#define LUMA1 0.2722287168
#define LUMA2 0.6740817658
#define LUMA3 0.0536895174

float saturate(float v) { return clamp(v, 0.0,       1.0);       }
vec2  saturate(vec2  v) { return clamp(v, vec2(0.0), vec2(1.0)); }
vec3  saturate(vec3  v) { return clamp(v, vec3(0.0), vec3(1.0)); }
vec4  saturate(vec4  v) { return clamp(v, vec4(0.0), vec4(1.0)); }

float LumaKey (vec3 color) {
    return dot(color, vec3(LUMA1, LUMA2, LUMA3)); 
}

vec3 ColorTemperatureToRGB(float temperatureInKelvins)
{
    vec3 retColor;
    
    temperatureInKelvins = clamp(temperatureInKelvins, 1000.0, 40000.0) / 100.0;
    
    if (temperatureInKelvins <= 66.0)
    {
        retColor.r = 1.0;
        retColor.g = saturate(0.39008157876901960784 * log(temperatureInKelvins) - 0.63184144378862745098);
    }
    else
    {
        float t = temperatureInKelvins - 60.0;
        retColor.r = saturate(1.29293618606274509804 * pow(t, -0.1332047592));
        retColor.g = saturate(1.12989086089529411765 * pow(t, -0.0755148492));
    }
    
    if (temperatureInKelvins >= 66.0)
        retColor.b = 1.0;
    else if(temperatureInKelvins <= 19.0)
        retColor.b = 0.0;
    else
        retColor.b = saturate(0.54320678911019607843 * log(temperatureInKelvins - 10.0) - 1.19625408914);

    return retColor;
}

float Luminance(vec3 color)
{
    float fmin = min(min(color.r, color.g), color.b);
    float fmax = max(max(color.r, color.g), color.b);
    return (fmax + fmin) / 2.0;
}

vec3 HUEtoRGB(float H)
{
    float R = abs(H * 6.0 - 3.0) - 1.0;
    float G = 2.0 - abs(H * 6.0 - 2.0);
    float B = 2.0 - abs(H * 6.0 - 4.0);
    return saturate(vec3(R,G,B));
}

vec3 HSLtoRGB(in vec3 HSL)
{
    vec3 RGB = HUEtoRGB(HSL.x);
    float C = (1.0 - abs(2.0 * HSL.z - 1.0)) * HSL.y;
    return (RGB - 0.5) * C + vec3(HSL.z);
}
 
vec3 RGBtoHCV(vec3 RGB)
{
    vec4 P = (RGB.g < RGB.b) ? vec4(RGB.bg, -1.0, 2.0/3.0) : vec4(RGB.gb, 0.0, -1.0/3.0);
    vec4 Q = (RGB.r < P.x) ? vec4(P.xyw, RGB.r) : vec4(RGB.r, P.yzx);
    float C = Q.x - min(Q.w, Q.y);
    float H = abs((Q.w - Q.y) / (6.0 * C + EPSILON) + Q.z);
    return vec3(H, C, Q.x);
}

vec3 RGBtoHSL(vec3 RGB)
{
    vec3 HCV = RGBtoHCV(RGB);
    float L = HCV.z - HCV.y * 0.5;
    float S = HCV.y / (1.0 - abs(L * 2.0 - 1.0) + EPSILON);
    return vec3(HCV.x, S, L);
}


vec3 ToneColorCorrection(vec3 Color, vec3 ColorSaturation, vec3 ColorContrast, vec3 ColorGamma, vec3 ColorGain, vec3 ColorOffset) {
    //First initialize the colorluma key
    float ColorLuma = LumaKey(Color);
    //Add the saturation with the above key
    Color = max(vec3(0,0,0), mix(ColorLuma.xxx, Color, ColorSaturation));
    //Contrast with slight color correction (0.18 coefficient)
    float ContrastCorrectionCoefficient = 0.18;
    Color = pow(Color * (1.0 / ContrastCorrectionCoefficient), ColorContrast) * ContrastCorrectionCoefficient;
    //Gamma
    Color = pow(Color, 1.0 / ColorGamma);
    //Gain and Offset
    Color = Color.rgb * ColorGain + (ColorOffset - 1);
    //Return the color corrected profile
    return Color;
}

vec3 FinalizeColorCorrection(vec3 Color, mat3 ColorSaturation, mat3 ColorContrast, mat3 ColorGamma, mat3 ColorGain, mat3 ColorOffset, vec2 Toneweights) {
    
    float CCShadowsMax = Toneweights.x;
    float CCHighlightsMin = Toneweights.y;

    //First initialize the colorluma key and set color correction weights
    float ColorLuma = LumaKey(Color);
    float CCWeightShadows = 1 - smoothstep(0, CCShadowsMax, ColorLuma);
    float CCWeightHighlights = smoothstep(CCHighlightsMin, 1, ColorLuma);
    float CCWeightMidtones = 1 - CCWeightShadows - CCWeightHighlights;

    vec3 CCColorShadows = ToneColorCorrection (
        Color,
        ColorSaturation[0],
        ColorContrast[0],
        ColorGamma[0],
        ColorGain[0],
        ColorOffset[0]
    );

    vec3 CCColorMidtones = ToneColorCorrection (
        Color,
        ColorSaturation[1],
        ColorContrast[1],
        ColorGamma[1],
        ColorGain[1],
        ColorOffset[1]
    );
    
    vec3 CCColorHighlights = ToneColorCorrection (
        Color,
        ColorSaturation[2],
        ColorContrast[2],
        ColorGamma[2],
        ColorGain[2],
        ColorOffset[2]
    );

    vec3 CombinedCCProfile = CCColorShadows * CCWeightShadows + CCColorMidtones * CCWeightMidtones + CCColorHighlights * CCWeightHighlights;

    return vec3(CombinedCCProfile);
}