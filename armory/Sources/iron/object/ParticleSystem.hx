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

class ParticleSystem {
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

	var ownerLoc = new Vec4();
	var ownerRot = new Quat();
	var ownerScl = new Vec4();

	var random = 0.0;

	public function new(sceneName: String, pref: TParticleReference) {
		seed = pref.seed;
		currentSpeed = speed;
		speed = 0;
		particles = [];
		ready = false;

		Data.getParticle(sceneName, pref.particle, function(b: ParticleData) {
			data = b;
			r = data.raw;

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

	public function update(object: MeshObject, owner: MeshObject) {
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

		updateGpu(object, owner);
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

	function updateGpu(object: MeshObject, owner: MeshObject) {
		if (!object.data.geom.instanced) setupGeomGpu(object, owner);
		// GPU particles transform is attached to owner object
	}

	function setupGeomGpu(object: MeshObject, owner: MeshObject) {
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

#elseif arm_cpu_particles
import iron.Scene;
import iron.data.Data;
import iron.data.ParticleData;
import iron.data.SceneFormat;
import iron.math.Quat;
import iron.math.Vec3;
import iron.math.Vec4;
import iron.object.MeshObject;
import iron.object.Object;
import iron.system.Time;
import iron.system.Tween;
import kha.FastFloat;
import kha.arrays.Int16Array;
import kha.arrays.Uint32Array;

class ParticleSystem {
    public var data: ParticleData;
    var r: TParticleData;

    // Format
    var frameRate: Float = 24.0;

    // Emission
    var count: Int = 10; // count
    var frameStart: Float = 1; // frame_start
    var frameEnd: Float = 10.0; // frame_end
    var lifetime: Float = 24.0; // lifetime
    var lifetimeRandom: Float = 0.0; // lifetime_random
    var emitFrom: Int = 1; // emit_from 0 - Vert, 1 - Face, 2 - Volume // TODO: fully integrate Blender's properties

    // Velocity
    var velocity: Vec3 = new Vec3(0.0, 0.0, 1.0); // object_align_factor: Float32Array
    var velocityRandom: Float = 0.0; // factor_random

    // Rotation // TODO: all rotations, starting with `rotation_mode`
    // var rotationVelocityHair: Bool = false; // TODO
    // var rotationDynamic: Bool = false; // TODO

    // Render
    var instanceObject: String; // instance_object
    var scale: Float = 1.0; // particle_size
    var scaleRandom: Float = 0.0; // size_random

    // TODO: scale over lifetime and color over lifetime
    // Field weights
    var gravity: Vec3 = new Vec3(0, 0, -9.8);
    var gravityFactor: Float = 0.0; // weight_gravity

    // Custom props
    var autoStart: Bool = true; // auto_start
    var loop: Bool = false; // loop

    // Internal logic
    var meshObject: MeshObject;
    var lifetimeSeconds: FastFloat = 0.0;
    var spawnRate: FastFloat = 0.0;
    var active: Bool = false;
    var c: Int = 0;
	var loopAnim: TAnim;
	var spawnAnim: TAnim;

    public function new(sceneName: String, pref: TParticleReference, mo: MeshObject) {
        Data.getParticle(sceneName, pref.particle, function (b: ParticleData) {
            data = b;
            r = data.raw;
			meshObject = mo;

			frameRate = r.fps;
            count = r.count;
            frameStart = r.frame_start;
            frameEnd = r.frame_end;
            lifetime = r.lifetime;
            lifetimeRandom = r.lifetime_random;
            emitFrom = r.emit_from;

            velocity = new Vec3(r.object_align_factor[0], r.object_align_factor[1], r.object_align_factor[2]).mult(frameRate / 24.0);
            velocityRandom = r.factor_random * (frameRate / 24.0);

            instanceObject = r.instance_object;

            scale = r.particle_size;
            scaleRandom = r.size_random;


            if (Scene.active.raw.gravity != null) {
                gravity = new Vec3(Scene.active.raw.gravity[0], Scene.active.raw.gravity[1], Scene.active.raw.gravity[2]).mult(frameRate / 24.0);
            }
            gravityFactor = r.weight_gravity * (frameRate / 24.0);

            autoStart = r.auto_start;
            loop = r.loop;

            // TODO: implement rest of the TParticleData

            spawnRate = ((frameEnd - frameStart) / count) / frameRate;
            lifetimeSeconds = lifetime / frameRate;

            if (autoStart) start();
        });
    }

    public function start() {
		c = 0;
		active = true;
        spawnParticle();
		if (loop) {
			loopAnim = Tween.timer(lifetimeSeconds, function () {
				if (spawnAnim != null) {
					Tween.stop(spawnAnim);
					spawnAnim = null;
				}
				start();
			});
		}
    }

    public function stop() {
        active = false;
        c = 0;

		if (loop) {
			if (loopAnim != null) {
				Tween.stop(loopAnim);
				loopAnim = null;
			}
		}

		if (spawnAnim != null) {
			Tween.stop(spawnAnim);
			spawnAnim = null;
		}
    }

    // TODO for optimization: create array containing all the particles and reuse them, instead of spawning and destroying them?
    function spawnParticle() {
		if (c >= count) {
			c = 0;
			active = false;
			return;
        }

        // Set the particle's rate
        spawnAnim = Tween.timer(spawnRate, function () {
            if (active) spawnParticle();
        });

        Scene.active.spawnObject(instanceObject, null, function (o: Object) {
            var objectPos: Vec4 = new Vec4();
            var objectRot: Quat = new Quat();
            var objectScale: Vec4 = new Vec4();
			meshObject.transform.world.decompose(objectPos, objectRot, objectScale);

            o.visible = true;
            meshObject.transform.buildMatrix();

            var normFactor: FastFloat = 1 / 32767;
            var scalePos: FastFloat = meshObject.data.scalePos;
            var scalePosParticle: FastFloat = cast(o, MeshObject).data.scalePos;
            var scaleFactor: Vec4  = new Vec4().setFrom(meshObject.transform.scale);
            scaleFactor.mult(scalePos / (scale * scalePosParticle));

			// TODO: add all properties from Blender's UI
            switch (emitFrom) {
                case 0: // Vertices
					var pa: TVertexArray = meshObject.data.geom.positions;
					var i: Int = Std.int(fhash(0) * (pa.values.length / pa.size));
					o.transform.loc.setFrom(new Vec4(pa.values[i * pa.size] * normFactor * scaleFactor.x, pa.values[i * pa.size + 1] * normFactor * scaleFactor.y, pa.values[i * pa.size + 2] * normFactor * scaleFactor.z, 1).add(objectPos));
                case 1: // Faces
                    var positions: Int16Array = meshObject.data.geom.positions.values;
                    var ia: Uint32Array = meshObject.data.geom.indices[Std.random(meshObject.data.geom.indices.length)];
                    var faceIndex: Int = Std.random(Std.int(ia.length / 3));

                    var i0 = ia[faceIndex * 3 + 0];
                    var i1 = ia[faceIndex * 3 + 1];
                    var i2 = ia[faceIndex * 3 + 2];

                    var v0: Vec3 = new Vec3(positions[i0 * 4], positions[i0 * 4 + 1], positions[i0 * 4 + 2]);
                    var v1: Vec3 = new Vec3(positions[i1 * 4], positions[i1 * 4 + 1], positions[i1 * 4 + 2]);
                    var v2: Vec3 = new Vec3(positions[i2 * 4], positions[i2 * 4 + 1], positions[i2 * 4 + 2]);

                    var pos: Vec3 = randomPointInTriangle(v0, v1, v2);

                    o.transform.loc.setFrom(new Vec4(pos.x * scaleFactor.x, pos.y * scaleFactor.y, pos.z * scaleFactor.z, 1).mult(normFactor).add(objectPos));
                case 2: // Volume
					var scaleFactorVolume: Vec4 = new Vec4().setFrom(o.transform.dim);
					scaleFactorVolume.mult(0.5 / (scale * scalePosParticle));
					o.transform.loc.setFrom(new Vec4((Math.random() * 2.0 - 1.0) * scaleFactorVolume.x, (Math.random() * 2.0 - 1.0) * scaleFactorVolume.y, (Math.random() * 2.0 - 1.0) * scaleFactorVolume.z, 1).add(objectPos));
            }

			o.transform.rot.setFrom(objectRot);
			o.transform.scale.setFrom(new Vec4(o.transform.scale.x / objectScale.x, o.transform.scale.y / objectScale.y, o.transform.scale.z / objectScale.z, 1.0).mult(scale).mult(1 - scaleRandom * Math.random()));
            o.transform.buildMatrix();

            var randomX: FastFloat = (Math.random() * 2 / scale - 1 / scale) * velocityRandom;
            var randomY: FastFloat = (Math.random() * 2 / scale - 1 / scale) * velocityRandom;
            var randomZ: FastFloat = (Math.random() * 2 / scale - 1 / scale) * velocityRandom;
            var g: Vec3 = new Vec3();

            var rotatedVelocity: Vec4 = new Vec4(velocity.x + randomX, velocity.y + randomY, velocity.z + randomZ, 1).applyQuat(objectRot);
            // if (rotationVelocityHair)  // TODO: use `rotation_mode`

            Tween.to({
                tick: function () {
                    g.add(gravity.clone().mult(0.5 * scale)).mult(Time.delta * gravityFactor);
                    rotatedVelocity.add(new Vec4(g.x, g.y, g.z, 1));
                    o.transform.translate(rotatedVelocity.x * Time.delta, rotatedVelocity.y * Time.delta, rotatedVelocity.z * Time.delta);
                    // if (rotationVelocityHair && rotationDynamic) { // TODO: use `rotation_mode`
                    //     // FIXME: this doesn't look correctly when the object's initial rotation isn't `Quat.identity()`, it has some weird rolling along the local Y axis.
                    //     var targetRot: Quat = new Quat().fromTo(new Vec4(0, -1, 0, 1), rotatedVelocity.clone().normalize());
                    //     o.transform.rot.setFrom(targetRot);
                    // }
                    o.transform.buildMatrix();
                },
                target: null,
                props: null,
                duration: lifetimeSeconds * (1 - Math.random() * lifetimeRandom),
                done: function () {
                    o.remove();
                }
            });

            c++;
        });
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
#end
