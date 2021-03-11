package armory.renderpath;

import kha.FastFloat;
import kha.graphics4.TextureFormat;
import kha.graphics4.Usage;

import iron.data.WorldData;

import armory.math.Helper;

class Nishita {

	public static var data: NishitaData = null;

	public static function recompute(world: WorldData) {
		if (world == null || world.raw.sun_direction == null) return;
		if (data == null) data = new NishitaData();

		// TODO
		data.recompute(1.0, 1.0, 1.0);
	}
}

class NishitaData {
	static inline var LUT_WIDTH = 16;

	/** Maximum ray height as defined by Cycles **/
	static inline var MAX_HEIGHT = 60000;

	static inline var RAYLEIGH_SCALE = 8e3;
	static inline var MIE_SCALE = 1.2e3;

	public var optDepthLUT: kha.Image;

	public function new() {}

	function getOzoneDensity(height: FastFloat): FastFloat {
		if (height < 10000.0 || height >= 40000.0) {
			return 0.0;
		}
		if (height < 25000.0) {
			return (height - 10000.0) / 15000.0;
		}
		return -((height - 40000.0) / 15000.0);
	}

	/**
		The RGBA texture layout looks as follows:
			R = Rayleigh optical depth at height \in [0, 60000]
			G = Mie optical depth at height \in [0, 60000]
			B = Ozone optical depth at height \in [0, 60000]
			A = Unused
	**/
	public function recompute(densityFacAir: FastFloat, densityFacDust: FastFloat, densityFacOzone: FastFloat) {
		optDepthLUT = kha.Image.create(LUT_WIDTH, 1, TextureFormat.RGBA32, Usage.StaticUsage);

		var textureData = optDepthLUT.lock();
		for (i in 0...LUT_WIDTH) {
			// Get the height for each LUT pixel i (in [-1, 1] range)
			var height = (i / LUT_WIDTH) * 2 - 1;

			// Use quadratic height for better horizon precision
			// See https://sebh.github.io/publications/egsr2020.pdf (5.3)
			height = 0.5 + 0.5 * Helper.sign(height) * Math.sqrt(Math.abs(height));
			height *= MAX_HEIGHT; // Denormalize

			// Make sure we use 32 bit floats
			var optDepthRayleigh: FastFloat = Math.exp(-height / RAYLEIGH_SCALE) * densityFacAir;
			var optDepthMie: FastFloat = Math.exp(-height / MIE_SCALE) * densityFacDust;
			var optDepthOzone: FastFloat = getOzoneDensity(height) * densityFacOzone;

			// 10 is the maximum density, so we divide by it to be able to use normalized values
			textureData.set(i * 4 + 0, Std.int(optDepthRayleigh * 255 / 10));
			textureData.set(i * 4 + 1, Std.int(optDepthMie * 255 / 10));
			textureData.set(i * 4 + 2, Std.int(optDepthOzone * 255 / 10));
			textureData.set(i * 4 + 3, 255); // Unused
		}
		optDepthLUT.unlock();
	}
}
