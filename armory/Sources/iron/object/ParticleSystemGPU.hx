package iron.object;

#if arm_gpu_particles
import kha.FastFloat;
import kha.graphics4.Usage;
import kha.arrays.Float32Array;
import iron.data.Data;
import iron.data.ParticleData;
import iron.data.SceneFormat;
import iron.system.Time;
import iron.math.Mat4;
import iron.math.Quat;
import iron.math.Vec3;
import iron.math.Vec4;

class ParticleSystemGPU {
	public var data: ParticleData;
	public var speed = 1.0;
	var currentSpeed = 0.0;
	var particles: Array<Particle>;
	var ready: Bool;
	var frameRate = 24;
	var lifetime = 0.0;
	var looptime = 0.0;
	var animtime = 0.0;
	var time = 0.0;
	var spawnRate = 0.0;
	var seed = 0;

	var r: TParticleData;
	var gx: Float;
	var gy: Float;
	var gz: Float;
	var alignx: Float;
	var aligny: Float;
	var alignz: Float;
	var dimx: Float;
	var dimy: Float;
	var tilesx: Int;
	var tilesy: Int;
	var tilesFramerate: Int;

	var count = 0;
	var lap = 0;
	var lapTime = 0.0;
	var m = Mat4.identity();

	var owner: MeshObject;
	var ownerLoc = new Vec4();
	var ownerRot = new Quat();
	var ownerScl = new Vec4();

	var random = 0.0;

	public function new(sceneName: String, pref: TParticleReference, mo: MeshObject) {
		seed = pref.seed;
		currentSpeed = speed;
		speed = 0;
		particles = [];
		ready = false;

		Data.getParticle(sceneName, pref.particle, function(b: ParticleData) {
			data = b;
			r = data.raw;
			owner = mo;
			owner.visible = owner.render_emitter; // use for mesh-material batch

			if (Scene.active.raw.gravity != null) {
				gx = Scene.active.raw.gravity[0] * r.weight_gravity;
				gy = Scene.active.raw.gravity[1] * r.weight_gravity;
				gz = Scene.active.raw.gravity[2] * r.weight_gravity;
			}
			else {
				gx = 0;
				gy = 0;
				gz = -9.81 * r.weight_gravity;
			}

			alignx = r.object_align_factor[0];
			aligny = r.object_align_factor[1];
			alignz = r.object_align_factor[2];

			looptime = (r.frame_end - r.frame_start) / frameRate;
			lifetime = r.lifetime / frameRate;
			animtime = r.loop ? looptime : looptime + lifetime;
			spawnRate = ((r.frame_end - r.frame_start) / r.count) / frameRate;

			for (i in 0...r.count) particles.push(new Particle(i));
			ready = true;

			if (r.auto_start) start();
		});
	}

	public function start() {
		if (r.is_unique) random = Math.random();
		lifetime = r.lifetime / frameRate;
		time = 0;
		lap = 0;
		lapTime = 0;
		speed = currentSpeed;
	}

	public function pause() {
		speed = 0;
	}

	public function resume() {
		lifetime = r.lifetime / frameRate;
		speed = currentSpeed;
	}

	// TODO: interrupt smoothly
	public function stop() {
		end();
	}

	function end() {
		lifetime = 0;
		speed = 0;
		lap = 0;
	}

	public function update(object: MeshObject) {
		if (!ready || object == null || speed == 0.0) return;
		if (iron.App.pauseUpdates) return;

		var prevLap = lap;

		// Copy owner world transform but discard scale
		owner.transform.world.decompose(ownerLoc, ownerRot, ownerScl);
		object.transform.loc = ownerLoc;
		object.transform.rot = ownerRot;

		// Set particle size per particle system
		object.transform.scale = new Vec4(r.particle_size, r.particle_size, r.particle_size, 1);

		object.transform.buildMatrix();
		owner.transform.buildMatrix();
		object.transform.dim.setFrom(owner.transform.dim);

		dimx = object.transform.dim.x;
		dimy = object.transform.dim.y;

		if (object.activeTilesheet != null) {
			tilesx = object.activeTilesheet.raw.tilesx;
			tilesy = object.activeTilesheet.raw.tilesy;
			tilesFramerate = object.activeTilesheet.raw.framerate;
		}

		// Animate
		time += Time.renderDelta * speed;
		lap = Std.int(time / animtime);
		lapTime = time - lap * animtime;
		count = Std.int(lapTime / spawnRate);

		if (lap > prevLap && !r.loop) {
			end();
		}

		updateGpu(object);
	}

	public function getData(): Mat4 {
		var hair = r.type == 1;
		m._00 = animtime;
		m._01 = hair ? 1 / particles.length : spawnRate;
		m._02 = hair ? 1 : lifetime;
		m._03 = particles.length;
		m._10 = hair ? 0 : alignx;
		m._11 = hair ? 0 : aligny;
		m._12 = hair ? 0 : alignz;
		m._13 = hair ? 0 : r.factor_random;
		m._20 = hair ? 0 : gx;
		m._21 = hair ? 0 : gy;
		m._22 = hair ? 0 : gz;
		m._23 = hair ? 0 : r.lifetime_random;
		m._30 = tilesx;
		m._31 = tilesy;
		m._32 = 1 / tilesFramerate;
		m._33 = hair ? 1 : lapTime;
		return m;
	}

	public function getSizeRandom(): FastFloat {
		return r.size_random;
	}

	public function getRandom(): FastFloat {
		return random;
	}

	public function getSize(): FastFloat {
		return r.particle_size;
	}

	function updateGpu(object: MeshObject) {
		if (!object.data.geom.instanced) setupGeomGpu(object);
		// GPU particles transform is attached to owner object
	}

	function setupGeomGpu(object: MeshObject) {
		var instancedData = new Float32Array(particles.length * 3);
		var i = 0;

		var normFactor = 1 / 32767; // pa.values are not normalized
		var scalePosOwner = owner.data.scalePos;
		var scalePosParticle = object.data.scalePos;
		var particleSize = r.particle_size;
		var scaleFactor = new Vec4().setFrom(owner.transform.scale);
		scaleFactor.mult(scalePosOwner / (particleSize * scalePosParticle));

		switch (r.emit_from) {
			case 0: // Vert
				var pa = owner.data.geom.positions;

				for (p in particles) {
					var j = Std.int(fhash(i) * (pa.values.length / pa.size));
					instancedData.set(i, pa.values[j * pa.size    ] * normFactor * scaleFactor.x); i++;
					instancedData.set(i, pa.values[j * pa.size + 1] * normFactor * scaleFactor.y); i++;
					instancedData.set(i, pa.values[j * pa.size + 2] * normFactor * scaleFactor.z); i++;
				}

			case 1: // Face
				var positions = owner.data.geom.positions.values;

				for (p in particles) {
					// Choose random index array (there is one per material) and random face
					var ia = owner.data.geom.indices[Std.random(owner.data.geom.indices.length)];
					var faceIndex = Std.random(Std.int(ia.length / 3));

					var i0 = ia[faceIndex * 3 + 0];
					var i1 = ia[faceIndex * 3 + 1];
					var i2 = ia[faceIndex * 3 + 2];

					var v0 = new Vec3(positions[i0 * 4], positions[i0 * 4 + 1], positions[i0 * 4 + 2]);
					var v1 = new Vec3(positions[i1 * 4], positions[i1 * 4 + 1], positions[i1 * 4 + 2]);
					var v2 = new Vec3(positions[i2 * 4], positions[i2 * 4 + 1], positions[i2 * 4 + 2]);

					var pos = randomPointInTriangle(v0, v1, v2);

					instancedData.set(i, pos.x * normFactor * scaleFactor.x); i++;
					instancedData.set(i, pos.y * normFactor * scaleFactor.y); i++;
					instancedData.set(i, pos.z * normFactor * scaleFactor.z); i++;
				}

			case 2: // Volume
				var scaleFactorVolume = new Vec4().setFrom(object.transform.dim);
				scaleFactorVolume.mult(0.5 / (particleSize * scalePosParticle));

				for (p in particles) {
					instancedData.set(i, (Math.random() * 2.0 - 1.0) * scaleFactorVolume.x); i++;
					instancedData.set(i, (Math.random() * 2.0 - 1.0) * scaleFactorVolume.y); i++;
					instancedData.set(i, (Math.random() * 2.0 - 1.0) * scaleFactorVolume.z); i++;
				}
		}
		object.data.geom.setupInstanced(instancedData, 1, Usage.StaticUsage);
	}

	function fhash(n: Int): Float {
		var s = n + 1.0;
		s *= 9301.0 % s;
		s = (s * 9301.0 + 49297.0) % 233280.0;
		return s / 233280.0;
	}

	public function remove() {}

	/**
		Generates a random point in the triangle with vertex positions abc.

		Please note that the given position vectors are changed in-place by this
		function and can be considered garbage afterwards, so make sure to clone
		them first if needed.
	**/
	public static inline function randomPointInTriangle(a: Vec3, b: Vec3, c: Vec3): Vec3 {
		// Generate a random point in a square where (0, 0) <= (x, y) < (1, 1)
		var x = Math.random();
		var y = Math.random();

		if (x + y > 1) {
			// We're in the upper right triangle in the square, mirror to lower left
			x = 1 - x;
			y = 1 - y;
		}

		// Transform the point to the triangle abc
		var u = b.sub(a);
		var v = c.sub(a);
		return a.add(u.mult(x).add(v.mult(y)));
	}
}

class Particle {
	public var i: Int;

	public var x = 0.0;
	public var y = 0.0;
	public var z = 0.0;

	public var cameraDistance: Float;

	public function new(i: Int) {
		this.i = i;
	}
}
#end
