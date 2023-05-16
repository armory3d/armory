package armory.renderpath;

import kha.FastFloat;
import kha.arrays.Float32Array;
import kha.graphics4.TextureFormat;
import kha.graphics4.Usage;

import iron.data.WorldData;
import iron.math.Vec2;
import iron.math.Vec3;

import armory.math.Helper;

/**
	Utility class to control the Nishita sky model.
**/
class Nishita {

	public static var data: NishitaData = null;

	/**
		Recomputes the nishita lookup table after the density settings changed.
		Do not call this method on every frame (it's slow)!
	**/
	public static function recompute(world: WorldData) {
		if (world == null || world.raw.nishita_density == null) return;
		if (data == null) data = new NishitaData();

		var density = world.raw.nishita_density;
		data.computeLUT(new Vec3(density[0], density[1], density[2]));
	}

	/** Sets the sky's density parameters and calls `recompute()` afterwards. **/
	public static function setDensity(world: WorldData, densityAir: FastFloat, densityDust: FastFloat, densityOzone: FastFloat) {
		if (world == null) return;

		if (world.raw.nishita_density == null) world.raw.nishita_density = new Float32Array(3);
		var density = world.raw.nishita_density;
		density[0] = Helper.clamp(densityAir, 0, 10);
		density[1] = Helper.clamp(densityDust, 0, 10);
		density[2] = Helper.clamp(densityOzone, 0, 10);

		recompute(world);
	}
}

/**
	This class holds the precalculated result of the inner scattering integral
	of the Nishita sky model. The outer integral is calculated in
	[`armory/Shaders/std/sky.glsl`](https://github.com/armory3d/armory/blob/master/Shaders/std/sky.glsl).

	@see `armory.renderpath.Nishita`
**/
class NishitaData {

	public var lut: kha.Image;

	/**
		The amount of individual sample heights stored in the LUT (and the width
		of the LUT image).
	**/
	public static var lutHeightSteps = 128;
	/**
		The amount of individual sun angle steps stored in the LUT (and the
		height of the LUT image).
	**/
	public static var lutAngleSteps = 128;

	/**
		Amount of steps for calculating the inner scattering integral. Heigher
		values are more precise but take longer to compute.
	**/
	public static var jSteps = 8;

	/** Radius of the atmosphere in kilometers. **/
	public static var radiusAtmo = 6420.0;
	/**
		Radius of the planet in kilometers. The default value is the earth radius as
		defined in Cycles.
	**/
	public static var radiusPlanet = 6360.0;

	/** Rayleigh scattering coefficient. **/
	public static var rayleighCoeff = new Vec3(5.5e-6, 13.0e-6, 22.4e-6);
	/** Rayleigh scattering scale parameter. **/
	public static var rayleighScale = 8e3;

	/** Mie scattering coefficient. **/
	public static var mieCoeff = 2e-5;
	/** Mie scattering scale parameter. **/
	public static var mieScale = 1.2e3;

	/** Ozone scattering coefficient. **/
	// The ozone absorption coefficients are taken from Cycles code.
	// Because Cycles calculates 21 wavelengths, we use the coefficients
	// which are closest to the RGB wavelengths (645nm, 510nm, 440nm).
	// Precalculating values by simulating Blender's spec_to_xyz() function
	// to include all 21 wavelengths gave unrealistic results.
	public static var ozoneCoeff = new Vec3(1.59051840791988e-6, 0.00000096707041180970, 0.00000007309568762914);

	public function new() {}

	/** Approximates the density of ozone for a given sample height. **/
	function getOzoneDensity(height: FastFloat): FastFloat {
		// Values are taken from Cycles code
		if (height < 10000.0 || height >= 40000.0) {
			return 0.0;
		}
		if (height < 25000.0) {
			return (height - 10000.0) / 15000.0;
		}
		return -((height - 40000.0) / 15000.0);
	}

	/**
		Ray-sphere intersection test that assumes the sphere is centered at the
		origin. There is no intersection when result.x > result.y. Otherwise
		this function returns the distances to the two intersection points,
		which might be equal.
	**/
	function raySphereIntersection(rayOrigin: Vec3, rayDirection: Vec3, sphereRadius: Float): Vec2 {
		// Algorithm is described here: https://en.wikipedia.org/wiki/Line%E2%80%93sphere_intersection
		var a = rayDirection.dot(rayDirection);
		var b = 2.0 * rayDirection.dot(rayOrigin);
		var c = rayOrigin.dot(rayOrigin) - (sphereRadius * sphereRadius);
		var d = (b * b) - 4.0 * a * c;

		// Ray does not intersect the sphere
		if (d < 0.0) return new Vec2(1e5, -1e5);

		return new Vec2(
			(-b - Math.sqrt(d)) / (2.0 * a),
			(-b + Math.sqrt(d)) / (2.0 * a)
		);
	}

	/**
		Computes the LUT texture for the given density values.
		@param density 3D vector of air density, dust density, ozone density
	**/
	public function computeLUT(density: Vec3) {
		var imageData = new haxe.io.Float32Array(lutHeightSteps * lutAngleSteps * 4);

		for (x in 0...lutHeightSteps) {
			var height = (x / (lutHeightSteps - 1));

			// Use quadratic height for better horizon precision
			height *= height;
			height *= radiusAtmo * 1000; // Denormalize height

			for (y in 0...lutAngleSteps) {
				var sunTheta = y / (lutAngleSteps - 1) * 2 - 1;

				// Improve horizon precision
				// See https://sebh.github.io/publications/egsr2020.pdf (5.3)
				sunTheta = Helper.sign(sunTheta) * sunTheta * sunTheta;
				sunTheta = sunTheta * Math.PI / 2 + Math.PI / 2; // Denormalize

				var jODepth = sampleSecondaryRay(height, sunTheta, density);

				var pixelIndex = (x + y * lutHeightSteps) * 4;
				imageData[pixelIndex + 0] = jODepth.x;
				imageData[pixelIndex + 1] = jODepth.y;
				imageData[pixelIndex + 2] = jODepth.z;
				imageData[pixelIndex + 3] = 1.0; // Unused
			}
		}

		lut = kha.Image.fromBytes(imageData.view.buffer, lutHeightSteps, lutAngleSteps, TextureFormat.RGBA128, Usage.StaticUsage);
	}

	/**
		Calculates the integral for the secondary ray.
	**/
	public function sampleSecondaryRay(height: FastFloat, sunTheta: FastFloat, density: Vec3): Vec3 {
		var radiusPlanetMeters = radiusPlanet * 1000;

		// Reconstruct values from the shader
		var iPos = new Vec3(0, 0, height + radiusPlanetMeters);
		var pSun = new Vec3(0.0, Math.sin(sunTheta), Math.cos(sunTheta)).normalize();

		var jTime: FastFloat = 0.0;
		// We compute the ray-sphere intersection in km to allow larger
		// atmosphere radii (radius is squared inside raySphereIntersection())
		var jStepSize: FastFloat = raySphereIntersection(iPos.clone().mult(0.001), pSun, radiusAtmo).y / jSteps;
		jStepSize *= 1000; // convert back to m

		// Optical depth accumulators for the secondary ray (Rayleigh, Mie, ozone)
		var jODepth = new Vec3();

		for (i in 0...jSteps) {

			// Calculate the secondary ray sample position and height
			var jPos = iPos.clone().add(pSun.clone().mult(jTime + jStepSize * 0.5));
			var jHeight = jPos.length() - radiusPlanetMeters;

			// Accumulate optical depth
			var optDepthRayleigh = Math.exp(-jHeight / rayleighScale) * density.x;
			var optDepthMie = Math.exp(-jHeight / mieScale) * density.y;
			var optDepthOzone = getOzoneDensity(jHeight) * density.z;
			jODepth.addf(optDepthRayleigh, optDepthMie, optDepthOzone);

			jTime += jStepSize;
		}

		jODepth.mult(jStepSize);

		// Precalculate a part of the secondary attenuation.
		// For one variable (e.g. x) in the vector, the formula is as follows:
		//
		// attn.x = exp(-(coeffX * (firstOpticalDepth.x + secondOpticalDepth.x)))
		//
		// We can split that up via:
		//
		// attn.x = exp(-(coeffX * firstOpticalDepth.x + coeffX * secondOpticalDepth.x))
		//        = exp(-(coeffX * firstOpticalDepth.x)) * exp(-(coeffX * secondOpticalDepth.x))
		//
		// The first factor of the resulting multiplication is calculated in the
		// shader, but we can already precalculate the second one. As a side
		// effect this keeps the range of the LUT values small because we don't
		// store the optical depth but the attenuation.
		var jAttenuation = new Vec3();
		var mie = mieCoeff * jODepth.y;
		jAttenuation.addf(mie, mie, mie);
		jAttenuation.add(rayleighCoeff.clone().mult(jODepth.x));
		jAttenuation.add(ozoneCoeff.clone().mult(jODepth.z));
		jAttenuation.exp(jAttenuation.mult(-1));

		return jAttenuation;
	}
}
