const float res = 50.0; // sdftex res

uniform sampler2D sdftex;

float mapsdf(vec3 ro, vec3 rd) {
	vec3 p = ro + rd;
	p = clamp(p, vec3(-1.0), vec3(1.0));
	p = p * 0.5 + 0.5;
	float s1 = (p.z * res);
	float s2 = int(s1);
	float s = s2 - s1;
	
	float m = sign(rd.z) > 0.0 ? s : (1.0 - s);
	vec2 co = vec2(p.x / res + s2 / res, p.y);
	float dist = (texture(sdftex, co).r) * m;
	
	co.x += 1 / res * sign(rd.z);
	dist += (texture(sdftex, co).r) * (1.0 - m);

	return dist;
}

float mapsdf2(vec3 p, vec3 rd) {
	// p = p * 0.5 + 0.5;
	// float s = int(p.z * res);
	// vec2 co = vec2(p.x / res + s / res, p.y);
	// return texture(sdftex, co).r;

	p = p * 0.5 + 0.5;
	float s1 = (p.z * res);
	float s2 = int(s1);
	float s = s2 - s1;

	float m = sign(rd.z) > 0.0 ? s : (1.0 - s);
	vec2 co = vec2(p.x / res + s2 / res, p.y);
	float dist = texture(sdftex, co).r * m;

	co.x += 1 / res * sign(rd.z);
	dist += (texture(sdftex, co).r) * (1.0 - m);

	return dist;
}

float sdBox(vec3 p, vec3 b) {
	vec3 d = abs(p) - b;
	return min(max(d.x, max(d.y, d.z)), 0.0) + length(max(d, 0.0));
}

float dfao(const vec3 p, const vec3 n) {
	float occ = 0.0;
	float sca = 1.0;
	for (int i = 0; i < 10; i++) {
		float r = 0.01 + 0.1 * float(i);
		vec3 rd = n * r;
		vec3 sp = rd + p;
		float d;
		if (sdBox(sp, vec3(1.0)) <= 0.0) {
			d = mapsdf(sp, rd);
		}
		else {
			vec3 sampleBorder = clamp(sp, vec3(-1.0), vec3(1.0)); 
			float phi = mapsdf2(sampleBorder, rd);
			float dd = 0.1;
			float grad_x = mapsdf2(sampleBorder + vec3(dd, 0, 0), rd) - phi;
			float grad_y = mapsdf2(sampleBorder + vec3(0, dd, 0), rd) - phi;
			vec3 grad = vec3(grad_x, grad_y, 1.0);
			vec3 endpoint = sampleBorder - normalize(grad) * phi;
			d = distance(endpoint, sp);
		}
		occ += (r - d) * sca;
		sca *= 0.85;
	}
	return clamp(1.0 - occ / (3.14), 0.0, 1.0);    
}
