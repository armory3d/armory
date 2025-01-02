/* Various sky functions
 * =====================
 *
 * Nishita model is based on https://github.com/wwwtyro/glsl-atmosphere (Unlicense License)
 *
 *   Changes to the original implementation:
 *     - r and pSun parameters of nishita_atmosphere() are already normalized
 *     - Some original parameters of nishita_atmosphere() are replaced with pre-defined values
 *     - Implemented air, dust and ozone density node parameters (see Blender source)
 *     - Replaced the inner integral calculation with a LUT lookup
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

#include "std/math.glsl"

uniform sampler2D nishitaLUT;
uniform vec2 nishitaDensity;

#ifndef PI
	#define PI 3.141592
#endif
#ifndef HALF_PI
	#define HALF_PI 1.570796
#endif

#define nishita_iSteps 16

// These values are taken from Cycles code if they
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

// Values from [Hill: 60]
#define sun_limb_darkening_col vec3(0.397, 0.503, 0.652)

vec3 nishita_lookupLUT(const float height, const float sunTheta) {
	vec2 coords = vec2(
		sqrt(height * (1 / nishita_atmo_radius)),
		0.5 + 0.5 * sign(sunTheta - HALF_PI) * sqrt(abs(sunTheta * (1 / HALF_PI) - 1))
	);
	return textureLod(nishitaLUT, coords, 0.0).rgb;
}

/* See raySphereIntersection() in armory/Sources/renderpath/Nishita.hx */
vec2 nishita_rsi(const vec3 r0, const vec3 rd, const float sr) {
	float a = dot(rd, rd);
	float b = 2.0 * dot(rd, r0);
	float c = dot(r0, r0) - (sr * sr);
	float d = (b*b) - 4.0*a*c;

	// If d < 0.0 the ray does not intersect the sphere
	return (d < 0.0) ? vec2(1e5,-1e5) : vec2((-b - sqrt(d))/(2.0*a), (-b + sqrt(d))/(2.0*a));
}

/*
 * r: normalized ray direction
 * r0: ray origin
 * pSun: normalized sun direction
 * rPlanet: planet radius
 */
vec3 nishita_atmosphere(const vec3 r, const vec3 r0, const vec3 pSun, const float rPlanet) {
	// Calculate the step size of the primary ray
	vec2 p = nishita_rsi(r0, r, nishita_atmo_radius);
	if (p.x > p.y) return vec3(0.0);
	p.y = min(p.y, nishita_rsi(r0, r, rPlanet).x);
	float iStepSize = (p.y - p.x) / float(nishita_iSteps);

	// Primary ray time
	float iTime = 0.0;

	// Accumulators for Rayleigh and Mie scattering.
	vec3 totalRlh = vec3(0,0,0);
	vec3 totalMie = vec3(0,0,0);

	// Optical depth accumulators for the primary ray
	float iOdRlh = 0.0;
	float iOdMie = 0.0;

	// Calculate the Rayleigh and Mie phases
	float mu = dot(r, pSun);
	float mumu = mu * mu;
	float pRlh = 3.0 / (16.0 * PI) * (1.0 + mumu);
	float pMie = 3.0 / (8.0 * PI) * ((1.0 - nishita_mie_dir_sq) * (mumu + 1.0)) / (pow(1.0 + nishita_mie_dir_sq - 2.0 * mu * nishita_mie_dir, 1.5) * (2.0 + nishita_mie_dir_sq));

	// Sample the primary ray
	for (int i = 0; i < nishita_iSteps; i++) {

		// Calculate the primary ray sample position and height
		vec3 iPos = r0 + r * (iTime + iStepSize * 0.5);
		float iHeight = length(iPos) - rPlanet;

		// Calculate the optical depth of the Rayleigh and Mie scattering for this step
		float odStepRlh = exp(-iHeight / nishita_rayleigh_scale) * nishitaDensity.x * iStepSize;
		float odStepMie = exp(-iHeight / nishita_mie_scale) * nishitaDensity.y * iStepSize;

		// Accumulate optical depth
		iOdRlh += odStepRlh;
		iOdMie += odStepMie;

		// Idea behind this: "Rotate" everything by iPos (-> iPos is the new zenith) and then all calculations for the
		// inner integral only depend on the sample height (iHeight) and sunTheta (angle between sun and new zenith).
		float sunTheta = safe_acos(dot(normalize(iPos), normalize(pSun)));
		vec3 jAttn = nishita_lookupLUT(iHeight, sunTheta);

		// Calculate attenuation
		vec3 iAttn = exp(-(
			nishita_mie_coeff * iOdMie
			+ nishita_rayleigh_coeff * iOdRlh
			// + 0 for ozone
		));
		vec3 attn = iAttn * jAttn;

		// Apply dithering to reduce visible banding
		attn *= 0.98 + rand(r.xy) * 0.04;

		// Accumulate scattering
		totalRlh += odStepRlh * attn;
		totalMie += odStepMie * attn;

		iTime += iStepSize;
	}

	return nishita_sun_intensity * (pRlh * nishita_rayleigh_coeff * totalRlh + pMie * nishita_mie_coeff * totalMie);
}

vec3 sun_disk(const vec3 n, const vec3 light_dir, const float disk_size, const float intensity) {
	// Normalized SDF
	float dist = distance(n, light_dir) / disk_size;

	// Darken the edges of the sun
	// [Hill: 28, 60] (according to [Nec96])
	float invDist = 1.0 - dist;
	float mu = sqrt(invDist * invDist);
	vec3 limb_darkening = 1.0 - (1.0 - pow(vec3(mu), sun_limb_darkening_col));

	return 1 + (1.0 - step(1.0, dist)) * nishita_sun_intensity * intensity * limb_darkening;
}

#endif
