/* Various sky functions
 * =====================
 *
 * Nishita model is based on https://github.com/wwwtyro/glsl-atmosphere(Unlicense License)
 *
 *   Changes to the original implementation:
 *     - r and pSun parameters of nishita_atmosphere() are already normalized
 *     - Some original parameters of nishita_atmosphere() are replaced with pre-defined values
 *     - Implemented air, dust and ozone density node parameters (see Blender source)
 *
 * Reference for the sun's limb darkening and ozone calculations:
 * [Hill] Sebastien Hillaire. Physically Based Sky, Atmosphere and Cloud Rendering in Frostbite
 * (https://media.contentapi.ea.com/content/dam/eacom/frostbite/files/s2016-pbs-frostbite-sky-clouds-new.pdf)
 *
 * Cycles code used for reference: blender/intern/sky/source/sky_nishita.cpp
 * (https://github.com/blender/blender/blob/4429b4b77ef6754739a3c2b4fabd0537999e9bdc/intern/sky/source/sky_nishita.cpp)
 */

#ifndef _SKY_GLSL_
#define _SKY_GLSL_

// OpenGl ES doesn't support 1D textures so we use a 1 px height sampler2D here...
uniform sampler2D nishitaLUT;

#define PI 3.141592

#define nishita_iSteps 16
#define nishita_jSteps 8

// The values here are taken from Cycles code if they
// exist there, otherwise they are taken from the example
// in the glsl-atmosphere repo
#define nishita_sun_intensity 22.0
#define nishita_atmo_radius 6420e3
#define nishita_rayleigh_scale 8e3
#define nishita_rayleigh_coeff vec3(5.5e-6, 13.0e-6, 22.4e-6)
#define nishita_mie_scale 1.2e3
#define nishita_mie_coeff 2e-5
#define nishita_mie_dir 0.76 // Aerosols anisotropy ("direction")
#define nishita_mie_dir_sq 0.5776 // Squared aerosols anisotropy

// The ozone absorption coefficients are taken from Cycles code.
// Because Cycles calculates 21 wavelengths, we use the coefficients
// which are closest to the RGB wavelengths (645nm, 510nm, 440nm).
// Precalculating values by simulating Blender's spec_to_xyz() function
// to include all 21 wavelengths gave unrealistic results
#define nishita_ozone_coeff vec3(1.59051840791988e-6, 0.00000096707041180970, 0.00000007309568762914)

// Values from [Hill: 60]
#define sun_limb_darkening_col vec3(0.397, 0.503, 0.652)

#define heightToLUT(h) (textureLod(nishitaLUT, vec2(clamp(h * (1 / 60000.0), 0.0, 1.0), 0.0), 0.0).xyz * 10.0)

/* Approximates the density of ozone for a given sample height. Values taken from Cycles code. */
float nishita_density_ozone(const float height) {
	return (height < 10000.0 || height >= 40000.0) ? 0.0 : (height < 25000.0 ? (height - 10000.0) / 15000.0 : -((height - 40000.0) / 15000.0));
}

/* ray-sphere intersection that assumes
 * the sphere is centered at the origin.
 * No intersection when result.x > result.y */
vec2 nishita_rsi(const vec3 r0, const vec3 rd, const float sr) {
	float a = dot(rd, rd);
	float b = 2.0 * dot(rd, r0);
	float c = dot(r0, r0) - (sr * sr);
	float d = (b*b) - 4.0*a*c;

	if (d < 0.0) return vec2(1e5,-1e5);
	return vec2(
		(-b - sqrt(d))/(2.0*a),
		(-b + sqrt(d))/(2.0*a)
	);
}

/*
 * r: normalized ray direction
 * r0: ray origin
 * pSun: normalized sun direction
 * rPlanet: planet radius
 * density: (air density, dust density, ozone density)
 */
vec3 nishita_atmosphere(const vec3 r, const vec3 r0, const vec3 pSun, const float rPlanet, const vec3 density) {
	// Calculate the step size of the primary ray.
	vec2 p = nishita_rsi(r0, r, nishita_atmo_radius);
	if (p.x > p.y) return vec3(0,0,0);
	p.y = min(p.y, nishita_rsi(r0, r, rPlanet).x);
	float iStepSize = (p.y - p.x) / float(nishita_iSteps);

	// Initialize the primary ray time.
	float iTime = 0.0;

	// Initialize accumulators for Rayleigh and Mie scattering.
	vec3 totalRlh = vec3(0,0,0);
	vec3 totalMie = vec3(0,0,0);

	// Initialize optical depth accumulators for the primary ray.
	float iOdRlh = 0.0;
	float iOdMie = 0.0;

	// Calculate the Rayleigh and Mie phases.
	float mu = dot(r, pSun);
	float mumu = mu * mu;
	float pRlh = 3.0 / (16.0 * PI) * (1.0 + mumu);
	float pMie = 3.0 / (8.0 * PI) * ((1.0 - nishita_mie_dir_sq) * (mumu + 1.0)) / (pow(1.0 + nishita_mie_dir_sq - 2.0 * mu * nishita_mie_dir, 1.5) * (2.0 + nishita_mie_dir_sq));

	// Sample the primary ray.
	for (int i = 0; i < nishita_iSteps; i++) {

		// Calculate the primary ray sample position.
		vec3 iPos = r0 + r * (iTime + iStepSize * 0.5);

		// Calculate the height of the sample.
		float iHeight = length(iPos) - rPlanet;

		// Calculate the optical depth of the Rayleigh and Mie scattering for this step.
		vec3 iLookup = heightToLUT(iHeight);
		float odStepRlh = iLookup.x * iStepSize;
		float odStepMie = iLookup.y * iStepSize;

		// Accumulate optical depth.
		iOdRlh += odStepRlh;
		iOdMie += odStepMie;

		// Calculate the step size of the secondary ray.
		float jStepSize = nishita_rsi(iPos, pSun, nishita_atmo_radius).y / float(nishita_jSteps);

		// Initialize the secondary ray time.
		float jTime = 0.0;

		// Initialize optical depth accumulators for the secondary ray.
		vec3 jODepth = vec3(0.0); // (Rayleigh, Mie, ozone)

		// Sample the secondary ray.
		for (int j = 0; j < nishita_jSteps; j++) {

			// Calculate the secondary ray sample position.
			vec3 jPos = iPos + pSun * (jTime + jStepSize * 0.5);

			// Calculate the height of the sample.
			float jHeight = length(jPos) - rPlanet;

			// Accumulate the optical depth.
			vec3 jLookup = heightToLUT(jHeight);
			jODepth += jLookup * jStepSize;

			// Increment the secondary ray time.
			jTime += jStepSize;
		}

		// Calculate attenuation.
		vec3 attn = exp(-(
			nishita_mie_coeff * (iOdMie + jODepth.y)
			+ (nishita_rayleigh_coeff) * (iOdRlh + jODepth.x)
			+ nishita_ozone_coeff * jODepth.z
		));

		// Accumulate scattering.
		totalRlh += odStepRlh * attn;
		totalMie += odStepMie * attn;

		// Increment the primary ray time.
		iTime += iStepSize;
	}

	// Calculate and return the final color.
	return nishita_sun_intensity * (pRlh * nishita_rayleigh_coeff * totalRlh + pMie * nishita_mie_coeff * totalMie);
}

vec3 sun_disk(const vec3 n, const vec3 light_dir, const float disk_size, const float intensity) {
	// Normalized SDF
	float dist = distance(n, light_dir) / disk_size;

	// Darken the edges of the sun
	// [Hill: 28, 60] (code from [Nec96])
	float invDist = 1.0 - dist;
	float mu = sqrt(invDist * invDist);
	vec3 limb_darkening = 1.0 - (1.0 - pow(vec3(mu), sun_limb_darkening_col));

	return 1 + (1.0 - step(1.0, dist)) * nishita_sun_intensity * intensity * limb_darkening;
}

#endif
