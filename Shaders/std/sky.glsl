/* Various sky functions
 * =====================
 *
 * Nishita model is based on https://github.com/wwwtyro/glsl-atmosphere(Unlicense License)
 *
 *   Changes to the original implementation:
 *     - r and pSun parameters of nishita_atmosphere() are already normalized
 *     - Some original parameters of nishita_atmosphere() are replaced with pre-defined values
 *     - Implemented air and dust density node parameters (see Blender source)
 */

#ifndef _SKY_GLSL_
#define _SKY_GLSL_

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
 * density: (air density, dust density)
 */
vec3 nishita_atmosphere(const vec3 r, const vec3 r0, const vec3 pSun, const float rPlanet, const vec2 density) {
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
		float odStepRlh = exp(-iHeight / nishita_rayleigh_scale) * density.x * iStepSize;
		float odStepMie = exp(-iHeight / nishita_mie_scale) * density.y * iStepSize;

		// Accumulate optical depth.
		iOdRlh += odStepRlh;
		iOdMie += odStepMie;

		// Calculate the step size of the secondary ray.
		float jStepSize = nishita_rsi(iPos, pSun, nishita_atmo_radius).y / float(nishita_jSteps);

		// Initialize the secondary ray time.
		float jTime = 0.0;

		// Initialize optical depth accumulators for the secondary ray.
		float jOdRlh = 0.0;
		float jOdMie = 0.0;

		// Sample the secondary ray.
		for (int j = 0; j < nishita_jSteps; j++) {

			// Calculate the secondary ray sample position.
			vec3 jPos = iPos + pSun * (jTime + jStepSize * 0.5);

			// Calculate the height of the sample.
			float jHeight = length(jPos) - rPlanet;

			// Accumulate the optical depth.
			jOdRlh += exp(-jHeight / nishita_rayleigh_scale) * density.x * jStepSize;
			jOdMie += exp(-jHeight / nishita_mie_scale) * density.y * jStepSize;

			// Increment the secondary ray time.
			jTime += jStepSize;
		}

		// Calculate attenuation.
		vec3 attn = exp(-(nishita_mie_coeff * (iOdMie + jOdMie) + nishita_rayleigh_coeff * (iOdRlh + jOdRlh)));

		// Accumulate scattering.
		totalRlh += odStepRlh * attn;
		totalMie += odStepMie * attn;

		// Increment the primary ray time.
		iTime += iStepSize;
	}

	// Calculate and return the final color.
	return nishita_sun_intensity * (pRlh * nishita_rayleigh_coeff * totalRlh + pMie * nishita_mie_coeff * totalMie);
}

#endif
