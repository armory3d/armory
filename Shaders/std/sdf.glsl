const float res = 50.0; // sdftex res

uniform sampler3D sdftex;

float mapsdf(vec3 p) {
	p = clamp(p, vec3(-1.0), vec3(1.0));
	p = p * 0.5 + 0.5;
	return texture(sdftex, p).a;
}

vec4 mapsdf2(vec3 p) {
	p = clamp(p, vec3(-1.0), vec3(1.0));
	p = p * 0.5 + 0.5;
	return texture(sdftex, p);
}

vec3 calcNormal(const vec3 pos, const float eps) {
	const vec3 v1 = vec3( 1.0,-1.0,-1.0);
	const vec3 v2 = vec3(-1.0,-1.0, 1.0);
	const vec3 v3 = vec3(-1.0, 1.0,-1.0);
	const vec3 v4 = vec3( 1.0, 1.0, 1.0);

	return normalize(v1 * mapsdf(pos + v1 * eps) +
					 v2 * mapsdf(pos + v2 * eps) +
					 v3 * mapsdf(pos + v3 * eps) +
					 v4 * mapsdf(pos + v4 * eps));
}

float sdBox(vec3 p, vec3 b) {
	vec3 d = abs(p) - b;
	return min(max(d.x, max(d.y, d.z)), 0.0) + length(max(d, 0.0));
}

float dfao(const vec3 p, const vec3 n) {
	const float eps = 0.02;
	float occ = 0.0;
	float sca = 1.0;
	for (int i = 0; i < 10; i++) {
		float r = 0.01 + 0.1 * float(i);
		vec3 rd = n * r;
		vec3 sp = rd + p;
		float d;
		if (sdBox(sp, vec3(1.0)) <= 0.0) {
			d = mapsdf(sp + rd);
			// if (d < eps) break;
		}
		else {
			vec3 sampleBorder = clamp(sp, vec3(-1.0), vec3(1.0)); 
			float phi = mapsdf(sampleBorder);
			float dd = 0.1;
			float grad_x = mapsdf(sampleBorder + vec3(dd, 0, 0)) - phi;
			float grad_y = mapsdf(sampleBorder + vec3(0, dd, 0)) - phi;
			vec3 grad = vec3(grad_x, grad_y, 1.0);
			vec3 endpoint = sampleBorder - normalize(grad) * phi;
			d = distance(endpoint, sp);
		}
		occ += (r - d) * sca;
		sca *= 0.85;
	}
	return clamp(1.0 - occ / (2.14), 0.0, 1.0);    
}

// float dfrs(const vec3 p, const vec3 l) {
float dfrs(const vec3 p, const vec3 l, const vec3 lp) {
	float visibility = 1.0;

	const float distmax = 10.0;
	const float eps = 0.01;
	float dist = 0.05;

	// float test = mapsdf(p);
	// if (test < 0.1) {
		// fragColor = vec4(1.0, 0.0, 0.0, 1.0);
		// return;
	// }

	// float lastd = distmax;
	for (int i = 0; i < 50; i++) {
		vec3 rd = l * dist;
		float d = sdBox(p + rd, vec3(1.0));

		// Going out of volume box
		// if (d > 0.0 && lastd < d) {
			// visibility = 1.0;
			// break;
		// }
		// lastd = d;

		if (d <= 0.0) { // In volume
			d = mapsdf(p + rd);

			// if (distance(p + rd, lp) < 0.05) { // Hits light pos
			if (dist + d > distance(p, lp) - 0.05) {
				// visibility = 1.0;
				break;
			}

			if (d < eps) {
				visibility = 0.0;
				break;
			}
		}
		else { // To volume
			// d += mapsdf(p + rd);

			vec3 sampleBorder = clamp(p + rd, vec3(-1.0), vec3(1.0)); 
			float phi = mapsdf(sampleBorder);
			float dd = 0.1;
			float grad_x = mapsdf(sampleBorder + vec3(dd, 0, 0)) - phi;
			float grad_y = mapsdf(sampleBorder + vec3(0, dd, 0)) - phi;
			vec3 grad = vec3(grad_x, grad_y, 1.0);
			vec3 endpoint = sampleBorder - normalize(grad) * phi;
			d = distance(endpoint, p + rd);

			// float dd = 0.1;
			// vec3 p0 = clamp(p, vec3(-1.0), vec3(1.0));
			// vec3 p1 = clamp(p, vec3(-0.99), vec3(0.99));
			// float r0 = mapsdf(p0);
			// float r1 = mapsdf(p1);
			// float h0 = 0.5 + (r0 * r0 - r1 * r1) / (2.0 * dd * dd);
			// float ri = sqrt(abs(r0 * r0 - h0 * h0 * dd * dd));
			// vec3 p2 = p0 + (p1 - p0) * h0;
			// vec3 p3 = p2 + vec3(p1.z - p0.z, p1.y - p0.y, p1.x - p0.x) * ri;
			// d = length((p + rd) - p3);
		}
		
		const float k = 4.0;
		visibility = min(visibility, k * d / dist);
		dist += d;
		
		if (dist > distmax) {
			break;
		}
	}

	return visibility;
}

vec3 orthogonal(const vec3 u) {
	// Pass normalized u
	const vec3 v = vec3(0.99146, 0.11664, 0.05832); // Pick any normalized vector
	return abs(dot(u, v)) > 0.99999 ? cross(u, vec3(0.0, 1.0, 0.0)) : cross(u, v);
}

vec3 traceCone(const vec3 p, const vec3 n) {
	vec3 col = vec3(0.0);
	
	const float eps = 0.02;
	float dist = 0.05;
	for (int i = 0; i < 10; i++) {
		vec3 rd = n * dist;
		float d = sdBox(p + rd, vec3(1.0));
		if (d <= 0.0) {
			vec4 res = mapsdf2(p + rd);
			d = res.a;
			if (d < eps) {
				// float vis = dfrs(p + rd, l, lp);
				// vec3 hitn = calcNormal(p + rd, 0.002);
				// float diffuse = max(0.0, dot(hitn, l));// / dot(l,l);
				col = res.rgb * max(1.0 - dist, 0.0);// * diffuse;// * vis;
				break;
			}
		}
		dist += d;
	}
	return col;
}

vec3 dfgi(const vec3 p, const vec3 n) {

	const float ANGLE_MIX = 0.5; // Angle mix (1.0f -> orthogonal direction, 0.0f -> direction of normal)
	const float w[3] = { 1.0, 1.0, 1.0 }; // Cone weights
	// Find a base for the side cones with the normal as one of its base vectors
	const vec3 ortho = normalize(orthogonal(n));
	const vec3 ortho2 = normalize(cross(ortho, n));
	// Find base vectors for the corner cones
	const vec3 corner = 0.5 * (ortho + ortho2);
	const vec3 corner2 = 0.5 * (ortho - ortho2);
	// Find start position of trace (start with a bit of offset)
	const vec3 offset = 0.0 * n;
	const vec3 origin = p + offset;

	vec3 col = vec3(0.0);

	const float CONE_OFFSET = 0.0;//-0.01;
	col += w[0] * traceCone(origin + CONE_OFFSET * n, n);

	const vec3 s1 = mix(n, ortho, ANGLE_MIX);
	const vec3 s2 = mix(n, -ortho, ANGLE_MIX);
	const vec3 s3 = mix(n, ortho2, ANGLE_MIX);
	const vec3 s4 = mix(n, -ortho2, ANGLE_MIX);
	col += w[1] * traceCone(origin + CONE_OFFSET * ortho, s1);
	col += w[1] * traceCone(origin - CONE_OFFSET * ortho, s2);
	col += w[1] * traceCone(origin + CONE_OFFSET * ortho2, s3);
	col += w[1] * traceCone(origin - CONE_OFFSET * ortho2, s4);

	const vec3 c1 = mix(n, corner, ANGLE_MIX);
	const vec3 c2 = mix(n, -corner, ANGLE_MIX);
	const vec3 c3 = mix(n, corner2, ANGLE_MIX);
	const vec3 c4 = mix(n, -corner2, ANGLE_MIX);
	col += w[2] * traceCone(origin + CONE_OFFSET * corner, c1);
	col += w[2] * traceCone(origin - CONE_OFFSET * corner, c2);
	col += w[2] * traceCone(origin + CONE_OFFSET * corner2, c3);
	col += w[2] * traceCone(origin - CONE_OFFSET * corner2, c4);

	return col / 9.0;
}
