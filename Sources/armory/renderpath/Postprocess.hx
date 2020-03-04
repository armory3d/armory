package armory.renderpath;

import iron.Scene;
import iron.object.Object;
import iron.data.MaterialData;
import iron.math.Vec4;

class Postprocess {

    public static var colorgrading_global_uniforms = [
        [6500.0, 1.0, 0.0],         //0: Whitebalance, Shadow Max, Highlight Min
        [1.0, 1.0, 1.0],            //1: Tint
        [1.0, 1.0, 1.0],            //2: Saturation
        [1.0, 1.0, 1.0],            //3: Contrast
        [1.0, 1.0, 1.0],            //4: Gamma
        [1.0, 1.0, 1.0],            //5: Gain
        [1.0, 1.0, 1.0],            //6: Offset
		[1.0, 1.0, 1.0]				//7: LUT Strength
    ];

    public static var colorgrading_shadow_uniforms = [
        [1.0, 1.0, 1.0], 			//0: Saturation
        [1.0, 1.0, 1.0], 			//1: Contrast
        [1.0, 1.0, 1.0], 			//2: Gamma
        [1.0, 1.0, 1.0], 			//3: Gain
        [1.0, 1.0, 1.0] 			//4: Offset
    ];

    public static var colorgrading_midtone_uniforms = [
        [1.0, 1.0, 1.0], 			//0: Saturation
        [1.0, 1.0, 1.0], 			//1: Contrast
        [1.0, 1.0, 1.0], 			//2: Gamma
        [1.0, 1.0, 1.0], 			//3: Gain
        [1.0, 1.0, 1.0] 			//4: Offset
    ];

    public static var colorgrading_highlight_uniforms = [
        [1.0, 1.0, 1.0], 			//0: Saturation
        [1.0, 1.0, 1.0], 			//1: Contrast
        [1.0, 1.0, 1.0], 			//2: Gamma
        [1.0, 1.0, 1.0], 			//3: Gain
        [1.0, 1.0, 1.0] 			//4: Offset
    ];

	public static var camera_uniforms = [
		1.0,				//0: Camera: F-Number
		2.8333,				//1: Camera: Shutter time
		100.0, 				//2: Camera: ISO
		0.0,				//3: Camera: Exposure Compensation
		0.01,				//4: Fisheye Distortion
		1,					//5: DoF AutoFocus §§ If true, it ignores the DoF Distance setting
		10.0,				//6: DoF Distance
		160.0,				//7: DoF Focal Length mm
		128,				//8: DoF F-Stop
		0,					//9: Tonemapping Method
		2.0					//10: Film Grain
	];

	public static var tonemapper_uniforms = [
		1.0, 				//0: Slope
		1.0, 				//1: Toe
		1.0, 				//2: Shoulder
		1.0, 				//3: Black Clip
		1.0 				//4: White Clip
	];

	public static var ssr_uniforms = [
		0.04,				//0: Step
		0.05,				//1: StepMin
		5.0,				//2: Search
		5.0,				//3: Falloff
		0.6					//4: Jitter
	];

	public static var bloom_uniforms = [
		1.0,				//0: Threshold
		3.5,				//1: Strength
		3.0					//2: Radius
	];

	public static var ssao_uniforms = [
		1.0,
		1.0,
		8
	];

	public static var lenstexture_uniforms = [
		0.1,				//0: Center Min Clip
		0.5,				//1: Center Max Clip
		0.1,				//2: Luminance Min
		2.5,				//3: Luminance Max
		2.0					//4: Brightness Exponent
	];

	public static var chromatic_aberration_uniforms = [
		2.0,				//0: Strength
		32					//1: Samples
	];

	public static function vec3Link(object:Object, mat:MaterialData, link:String):iron.math.Vec4 {
        var v:Vec4 = null;

		if (link == "_globalWeight") {
			var ppm_index = 0;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_global_uniforms[ppm_index][0];
			v.y = colorgrading_global_uniforms[ppm_index][1];
			v.z = colorgrading_global_uniforms[ppm_index][2];
		}
		if (link == "_globalTint") {
			var ppm_index = 1;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_global_uniforms[ppm_index][0];
			v.y = colorgrading_global_uniforms[ppm_index][1];
			v.z = colorgrading_global_uniforms[ppm_index][2];
		}
		if (link == "_globalSaturation") {
			var ppm_index = 2;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_global_uniforms[ppm_index][0];
			v.y = colorgrading_global_uniforms[ppm_index][1];
			v.z = colorgrading_global_uniforms[ppm_index][2];
		}
		if (link == "_globalContrast") {
			var ppm_index = 3;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_global_uniforms[ppm_index][0];
			v.y = colorgrading_global_uniforms[ppm_index][1];
			v.z = colorgrading_global_uniforms[ppm_index][2];
		}
		if (link == "_globalGamma") {
			var ppm_index = 4;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_global_uniforms[ppm_index][0];
			v.y = colorgrading_global_uniforms[ppm_index][1];
			v.z = colorgrading_global_uniforms[ppm_index][2];
		}
		if (link == "_globalGain") {
			var ppm_index = 5;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_global_uniforms[ppm_index][0];
			v.y = colorgrading_global_uniforms[ppm_index][1];
			v.z = colorgrading_global_uniforms[ppm_index][2];
		}
		if (link == "_globalOffset") {
			var ppm_index = 6;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_global_uniforms[ppm_index][0];
			v.y = colorgrading_global_uniforms[ppm_index][1];
			v.z = colorgrading_global_uniforms[ppm_index][2];
		}

		//Shadow ppm
		if (link == "_shadowSaturation") {
			var ppm_index = 0;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_shadow_uniforms[ppm_index][0];
			v.y = colorgrading_shadow_uniforms[ppm_index][1];
			v.z = colorgrading_shadow_uniforms[ppm_index][2];
		}
		if (link == "_shadowContrast") {
			var ppm_index = 1;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_shadow_uniforms[ppm_index][0];
			v.y = colorgrading_shadow_uniforms[ppm_index][1];
			v.z = colorgrading_shadow_uniforms[ppm_index][2];
		}
		if (link == "_shadowGamma") {
			var ppm_index = 2;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_shadow_uniforms[ppm_index][0];
			v.y = colorgrading_shadow_uniforms[ppm_index][1];
			v.z = colorgrading_shadow_uniforms[ppm_index][2];
		}
		if (link == "_shadowGain") {
			var ppm_index = 3;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_shadow_uniforms[ppm_index][0];
			v.y = colorgrading_shadow_uniforms[ppm_index][1];
			v.z = colorgrading_shadow_uniforms[ppm_index][2];
		}
		if (link == "_shadowOffset") {
			var ppm_index = 4;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_shadow_uniforms[ppm_index][0];
			v.y = colorgrading_shadow_uniforms[ppm_index][1];
			v.z = colorgrading_shadow_uniforms[ppm_index][2];
		}

		//Midtone ppm
		if (link == "_midtoneSaturation") {
			var ppm_index = 0;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_midtone_uniforms[ppm_index][0];
			v.y = colorgrading_midtone_uniforms[ppm_index][1];
			v.z = colorgrading_midtone_uniforms[ppm_index][2];
		}
		if (link == "_midtoneContrast") {
			var ppm_index = 1;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_midtone_uniforms[ppm_index][0];
			v.y = colorgrading_midtone_uniforms[ppm_index][1];
			v.z = colorgrading_midtone_uniforms[ppm_index][2];
		}
		if (link == "_midtoneGamma") {
			var ppm_index = 2;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_midtone_uniforms[ppm_index][0];
			v.y = colorgrading_midtone_uniforms[ppm_index][1];
			v.z = colorgrading_midtone_uniforms[ppm_index][2];
		}
		if (link == "_midtoneGain") {
			var ppm_index = 3;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_midtone_uniforms[ppm_index][0];
			v.y = colorgrading_midtone_uniforms[ppm_index][1];
			v.z = colorgrading_midtone_uniforms[ppm_index][2];
		}
		if (link == "_midtoneOffset") {
			var ppm_index = 4;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_midtone_uniforms[ppm_index][0];
			v.y = colorgrading_midtone_uniforms[ppm_index][1];
			v.z = colorgrading_midtone_uniforms[ppm_index][2];
		}

		//Highlight ppm
		if (link == "_highlightSaturation") {
			var ppm_index = 0;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_highlight_uniforms[ppm_index][0];
			v.y = colorgrading_highlight_uniforms[ppm_index][1];
			v.z = colorgrading_highlight_uniforms[ppm_index][2];
		}
		if (link == "_highlightContrast") {
			var ppm_index = 1;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_highlight_uniforms[ppm_index][0];
			v.y = colorgrading_highlight_uniforms[ppm_index][1];
			v.z = colorgrading_highlight_uniforms[ppm_index][2];
		}
		if (link == "_highlightGamma") {
			var ppm_index = 2;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_highlight_uniforms[ppm_index][0];
			v.y = colorgrading_highlight_uniforms[ppm_index][1];
			v.z = colorgrading_highlight_uniforms[ppm_index][2];
		}
		if (link == "_highlightGain") {
			var ppm_index = 3;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_highlight_uniforms[ppm_index][0];
			v.y = colorgrading_highlight_uniforms[ppm_index][1];
			v.z = colorgrading_highlight_uniforms[ppm_index][2];
		}
		if (link == "_highlightOffset") {
			var ppm_index = 4;
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_highlight_uniforms[ppm_index][0];
			v.y = colorgrading_highlight_uniforms[ppm_index][1];
			v.z = colorgrading_highlight_uniforms[ppm_index][2];
		}

		//Postprocess Components
		if (link == "_PPComp1") {
			v = iron.object.Uniforms.helpVec;
			v.x = camera_uniforms[0]; //F-Number
			v.y = camera_uniforms[1]; //Shutter
			v.z = camera_uniforms[2]; //ISO
		}

		if (link == "_PPComp2") {
			v = iron.object.Uniforms.helpVec;
			v.x = camera_uniforms[3]; //EC
			v.y = camera_uniforms[4]; //Lens Distortion
			v.z = camera_uniforms[5]; //DOF Autofocus
		}

		if (link == "_PPComp3") {
			v = iron.object.Uniforms.helpVec;
			v.x = camera_uniforms[6]; //Distance
			v.y = camera_uniforms[7]; //Focal Length
			v.z = camera_uniforms[8]; //F-Stop
		}

		if (link == "_PPComp4") {
			v = iron.object.Uniforms.helpVec;
			v.x = Std.int(camera_uniforms[9]); //Tonemapping
			v.y = camera_uniforms[10]; //Film Grain
			v.z = tonemapper_uniforms[0]; //Slope
		}

		if (link == "_PPComp5") {
			v = iron.object.Uniforms.helpVec;
			v.x = tonemapper_uniforms[1]; //Toe
			v.y = tonemapper_uniforms[2]; //Shoulder
			v.z = tonemapper_uniforms[3]; //Black Clip
		}

		if (link == "_PPComp6") {
			v = iron.object.Uniforms.helpVec;
			v.x = tonemapper_uniforms[4]; //White Clip
			v.y = lenstexture_uniforms[0]; //Center Min
			v.z = lenstexture_uniforms[1]; //Center Max
		}

		if (link == "_PPComp7") {
			v = iron.object.Uniforms.helpVec;
			v.x = lenstexture_uniforms[2]; //Lum min
			v.y = lenstexture_uniforms[3]; //Lum max
			v.z = lenstexture_uniforms[4]; //Expo
		}

		if (link == "_PPComp8") {
			v = iron.object.Uniforms.helpVec;
			v.x = colorgrading_global_uniforms[7][0]; //LUT R
			v.y = colorgrading_global_uniforms[7][1]; //LUT G
			v.z = colorgrading_global_uniforms[7][2]; //LUT B
		}

		if (link == "_PPComp9") {
			v = iron.object.Uniforms.helpVec;
			v.x = ssr_uniforms[0]; //Step
			v.y = ssr_uniforms[1]; //StepMin
			v.z = ssr_uniforms[2]; //Search
		}
		
		if (link == "_PPComp10") {
			v = iron.object.Uniforms.helpVec;
			v.x = ssr_uniforms[3]; //Falloff
			v.y = ssr_uniforms[4]; //Jitter
			v.z = bloom_uniforms[0]; //Bloom Threshold
		}

		if (link == "_PPComp11") {
			v = iron.object.Uniforms.helpVec;
			v.x = bloom_uniforms[1]; //Bloom Strength
			v.y = bloom_uniforms[2]; //Bloom Radius
			v.z = ssao_uniforms[0]; //SSAO Strength
		}

		if (link == "_PPComp12") {
			v = iron.object.Uniforms.helpVec;
			v.x = ssao_uniforms[1]; //SSAO Radius
			v.y = ssao_uniforms[2]; //SSAO Max Steps
			v.z = 0;
		}

		if(link == "_PPComp13") {
			v = iron.object.Uniforms.helpVec;
			v.x = chromatic_aberration_uniforms[0]; //CA Strength
			v.y = chromatic_aberration_uniforms[1]; //CA Samples
			v.z = 0;
		}

    public static function init() {

		iron.object.Uniforms.externalVec3Links.push(vec3Link);

    }

}