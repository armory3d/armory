package armory.logicnode;

import iron.math.Vec4;

class ColorMixNode extends LogicNode {

	var SIZE:Int = 38;
	var GAMMA:Float = 2.4;
    var EPSILON:Float = 0.00000001;
    
    var SPD_C:Array<Float> = [0.96853629, 0.96855103, 0.96859338, 0.96877345, 0.96942204, 0.97143709, 0.97541862, 0.98074186, 0.98580992, 0.98971194, 0.99238027, 0.99409844, 0.995172, 0.99576545, 0.99593552, 0.99564041, 0.99464769, 0.99229579, 0.98638762, 0.96829712, 0.89228016, 0.53740239, 0.15360445, 0.05705719, 0.03126539, 0.02205445, 0.01802271, 0.0161346, 0.01520947, 0.01475977, 0.01454263, 0.01444459, 0.01439897, 0.0143762, 0.01436343, 0.01435687, 0.0143537, 0.01435408];
    var SPD_M:Array<Float> = [0.51567122, 0.5401552, 0.62645502, 0.75595012, 0.92826996, 0.97223624, 0.98616174, 0.98955255, 0.98676237, 0.97312575, 0.91944277, 0.32564851, 0.13820628, 0.05015143, 0.02912336, 0.02421691, 0.02660696, 0.03407586, 0.04835936, 0.0001172, 0.00008554, 0.85267882, 0.93188793, 0.94810268, 0.94200977, 0.91478045, 0.87065445, 0.78827548, 0.65738359, 0.59909403, 0.56817268, 0.54031997, 0.52110241, 0.51041094, 0.50526577, 0.5025508, 0.50126452, 0.50083021];
    var SPD_Y:Array<Float> = [0.02055257, 0.02059936, 0.02062723, 0.02073387, 0.02114202, 0.02233154, 0.02556857, 0.03330189, 0.05185294, 0.10087639, 0.24000413, 0.53589066, 0.79874659, 0.91186529, 0.95399623, 0.97137099, 0.97939505, 0.98345207, 0.98553736, 0.98648905, 0.98674535, 0.98657555, 0.98611877, 0.98559942, 0.98507063, 0.98460039, 0.98425301, 0.98403909, 0.98388535, 0.98376116, 0.98368246, 0.98365023, 0.98361309, 0.98357259, 0.98353856, 0.98351247, 0.98350101, 0.98350852];
	var SPD_R:Array<Float> = [0.03147571, 0.03146636, 0.03140624, 0.03119611, 0.03053888, 0.02856855, 0.02459485, 0.0192952, 0.01423112, 0.01033111, 0.00765876, 0.00593693, 0.00485616, 0.00426186, 0.00409039, 0.00438375, 0.00537525, 0.00772962, 0.0136612, 0.03181352, 0.10791525, 0.46249516, 0.84604333, 0.94275572, 0.96860996, 0.97783966, 0.98187757, 0.98377315, 0.98470202, 0.98515481, 0.98537114, 0.98546685, 0.98550011, 0.98551031, 0.98550741, 0.98551323, 0.98551563, 0.98551547];
	var SPD_G:Array<Float> = [0.49108579, 0.46944057, 0.4016578, 0.2449042, 0.0682688, 0.02732883, 0.013606, 0.01000187, 0.01284127, 0.02636635, 0.07058713, 0.70421692, 0.85473994, 0.95081565, 0.9717037, 0.97651888, 0.97429245, 0.97012917, 0.9425863, 0.99989207, 0.99989891, 0.13823139, 0.06968113, 0.05628787, 0.06111561, 0.08987709, 0.13656016, 0.22169624, 0.32176956, 0.36157329, 0.4836192, 0.46488579, 0.47440306, 0.4857699, 0.49267971, 0.49625685, 0.49807754, 0.49889859];
	var SPD_B:Array<Float> = [0.97901834, 0.97901649, 0.97901118, 0.97892146, 0.97858555, 0.97743705, 0.97428075, 0.96663223, 0.94822893, 0.89937713, 0.76070164, 0.4642044, 0.20123039, 0.08808402, 0.04592894, 0.02860373, 0.02060067, 0.01656701, 0.01451549, 0.01357964, 0.01331243, 0.01347661, 0.01387181, 0.01435472, 0.01479836, 0.0151525, 0.01540513, 0.01557233, 0.0156571, 0.01571025, 0.01571916, 0.01572133, 0.01572502, 0.01571717, 0.01571905, 0.01571059, 0.01569728, 0.0157002];
	var CIE_CMF_X:Array<Float> = [0.00006469, 0.00021941, 0.00112057, 0.00376661, 0.01188055, 0.02328644, 0.03455942, 0.03722379, 0.03241838, 0.02123321, 0.01049099, 0.00329584, 0.00050704, 0.00094867, 0.00627372, 0.01686462, 0.02868965, 0.04267481, 0.05625475, 0.0694704, 0.08305315, 0.0861261, 0.09046614, 0.08500387, 0.07090667, 0.05062889, 0.03547396, 0.02146821, 0.01251646, 0.00680458, 0.00346457, 0.00149761, 0.0007697, 0.00040737, 0.00016901, 0.00009522, 0.00004903, 0.00002];
	var CIE_CMF_Y:Array<Float> = [0.00000184, 0.00000621, 0.00003101, 0.00010475, 0.00035364, 0.00095147, 0.00228226, 0.00420733, 0.0066888, 0.0098884, 0.01524945, 0.02141831, 0.03342293, 0.05131001, 0.07040208, 0.08783871, 0.09424905, 0.09795667, 0.09415219, 0.08678102, 0.07885653, 0.0635267, 0.05374142, 0.04264606, 0.03161735, 0.02088521, 0.01386011, 0.00810264, 0.0046301, 0.00249138, 0.0012593, 0.00054165, 0.00027795, 0.00014711, 0.00006103, 0.00003439, 0.00001771, 0.00000722];
	var CIE_CMF_Z:Array<Float> = [0.00030502, 0.00103681, 0.00531314, 0.01795439, 0.05707758, 0.11365162, 0.17335873, 0.19620658, 0.18608237, 0.13995048, 0.08917453, 0.04789621, 0.02814563, 0.01613766, 0.0077591, 0.00429615, 0.00200551, 0.00086147, 0.00036904, 0.00019143, 0.00014956, 0.00009231, 0.00006813, 0.00002883, 0.00001577, 0.00000394, 0.00000158, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
	var XYZ_RGB:Array<Array<Float>> = [[3.24306333, -1.53837619, -0.49893282], [-0.96896309, 1.87542451, 0.04154303], [0.05568392, -0.20417438, 1.05799454]];

	public function linearToConcentration(l1:Float, l2:Float, t:Float):Float {
        var t1 = l1 * Math.pow(1 - t, 2);
        var t2 = l2 * Math.pow(t, 2);
        return t2 / (t1 + t2);
    }

    public function spectralMix(color1:Array<Int>, color2:Array<Int>, t:Float):Array<Int> {
        var lrgb1 = srgbToLinear(color1);
        var lrgb2 = srgbToLinear(color2);

        var R1 = linearToReflectance(lrgb1);
        var R2 = linearToReflectance(lrgb2);

        var l1 = dotProduct(R1, CIE_CMF_Y);
        var l2 = dotProduct(R2, CIE_CMF_Y);

        t = linearToConcentration(l1, l2, t);

        var R:Array<Float> = new Array<Float>();
        for (i in 0...SIZE) {
            var KS = (1 - t) * Math.pow((1 - R1[i]), 2) / (2 * R1[i]) + t * Math.pow((1 - R2[i]), 2) / (2 * R2[i]);
            var KM = 1 + KS - Math.sqrt(KS * KS + 2 * KS);
            R.push(KM);
        }

        var xyz = reflectanceToXYZ(R);
        return xyzToSrgb(xyz);
    }

    public function uncompand(x:Float):Float {
        return x < 0.04045 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, GAMMA);
    }

    public function compand(x:Float):Float {
        return x < 0.0031308 ? x * 12.92 : 1.055 * Math.pow(x, 1.0 / GAMMA) - 0.055;
    }

    public function srgbToLinear(srgb:Array<Int>):Array<Float> {
        var r = uncompand(srgb[0] / 255);
        var g = uncompand(srgb[1] / 255);
        var b = uncompand(srgb[2] / 255);
        return [r, g, b];
    }

    public function linearToSrgb(lrgb:Array<Float>):Array<Int> {
        var r = compand(lrgb[0]);
        var g = compand(lrgb[1]);
        var b = compand(lrgb[2]);
        return [Math.round(clamp(r, 0, 1) * 255), Math.round(clamp(g, 0, 1) * 255), Math.round(clamp(b, 0, 1) * 255)];
    }

    public function reflectanceToXYZ(R:Array<Float>):Array<Float> {
        var x = dotProduct(R, CIE_CMF_X);
        var y = dotProduct(R, CIE_CMF_Y);
        var z = dotProduct(R, CIE_CMF_Z);
        return [x, y, z];
    }

    public function xyzToSrgb(xyz:Array<Float>):Array<Int> {
        var r = dotProduct(XYZ_RGB[0], xyz);
        var g = dotProduct(XYZ_RGB[1], xyz);
        var b = dotProduct(XYZ_RGB[2], xyz);
        return linearToSrgb([r, g, b]);
    }

    public function spectralUpsampling(lrgb:Array<Float>):Array<Float> {
        var w = Math.min(Math.min(lrgb[0], lrgb[1]), lrgb[2]);

        var lrgbNew = [lrgb[0] - w, lrgb[1] - w, lrgb[2] - w];

        var c = Math.min(lrgbNew[1], lrgbNew[2]);
        var m = Math.min(lrgbNew[0], lrgbNew[2]);
        var y = Math.min(lrgbNew[0], lrgbNew[1]);
        var r = Math.max(0, Math.min(lrgbNew[0] - lrgbNew[2], lrgbNew[0] - lrgbNew[1]));
        var g = Math.max(0, Math.min(lrgbNew[1] - lrgbNew[2], lrgbNew[1] - lrgbNew[0]));
        var b = Math.max(0, Math.min(lrgbNew[2] - lrgbNew[1], lrgbNew[2] - lrgbNew[0]));

        return [w, c, m, y, r, g, b];
    }

    public function linearToReflectance(lrgb:Array<Float>):Array<Float> {
        var weights = spectralUpsampling(lrgb);

        var R:Array<Float> = new Array<Float>();
        for (i in 0...SIZE) {
            R[i] = Math.max(EPSILON,
                weights[0]
                + weights[1] * SPD_C[i]
                + weights[2] * SPD_M[i]
                + weights[3] * SPD_Y[i]
                + weights[4] * SPD_R[i]
                + weights[5] * SPD_G[i]
                + weights[6] * SPD_B[i]
            );
        }

        return R;
    }

    public function dotProduct(a:Array<Float>, b:Array<Float>):Float {
        var sum:Float = 0;
        for (i in 0...a.length) {
            sum += a[i] * b[i];
        }
        return sum;
    }

    public function clamp(value:Float, minValue:Float, maxValue:Float):Float {
        return Math.min(Math.max(value, minValue), maxValue);
    }

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var Color1:Vec4 = inputs[0].get();
		var Color2:Vec4 = inputs[1].get();
		var mix:Float = inputs[2].get();

        mix = Math.min(Math.max(mix, 0), 1);

		var col1 = [Std.int(Color1.x*255), Std.int(Color1.y*255), Std.int(Color1.z*255)];
		var col2 = [Std.int(Color2.x*255), Std.int(Color2.y*255), Std.int(Color2.z*255)];

		var ColorMix = spectralMix(col1, col2, mix);

		return new Vec4(ColorMix[0]/255, ColorMix[1]/255, ColorMix[2]/255, (Color1.w+Color2.w)/2);
	}
}
