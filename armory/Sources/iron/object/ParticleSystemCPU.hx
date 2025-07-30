package iron.object;

#if arm_cpu_particles
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

class ParticleSystemCPU {
    public var data: ParticleData;
	public var speed: FastFloat = 1.0; // Not used yet. Added to go in hand with `ParticleSystemGPU`
    var r: TParticleData;

    // Format
	final baseFrameRate: FastFloat = 24.0;
    var frameRate: FastFloat = 24.0;

    // Emission
	var type: Int = 0; // type: 0 - Emission, 1 - Hair
    var count: Int = 10; // count
    var frameStart: FastFloat = 1; // frame_start
    var frameEnd: FastFloat = 10.0; // frame_end
    var lifetime: FastFloat = 24.0; // lifetime
    var lifetimeRandom: FastFloat = 0.0; // lifetime_random
    var emitFrom: Int = 1; // emit_from: 0 - Vert, 1 - Face, 2 - Volume // TODO: fully integrate Blender's properties

    // Velocity
    var velocity: Vec3 = new Vec3(0.0, 0.0, 1.0); // object_align_factor: Float32Array
    var velocityRandom: FastFloat = 0.0; // factor_random

    // Rotation
	var rotation: Bool = false; // use_rotations
	var orientationAxis: Int = 0; // rotation_mode: 0 - None, 1 - Normal, 2 - Normal-Tangent, 3 - Velocity/Hair, 4 - Global X, 5 - Global Y, 6 - Global Z, 7 - Object X, 8 - Object Y, 9 - Object Z
	var rotationRandom: FastFloat = 0.0; // rotation_factor_random
	var phase: FastFloat = 0.0; // phase_factor
	var phaseRandom: FastFloat = 0.0; // phase_factor_random
	var dynamicRotation: Bool = false; // use_dynamic_rotation

    // Render
    var instanceObject: String; // instance_object
    var scale: FastFloat = 1.0; // particle_size
    var scaleRandom: FastFloat = 0.0; // size_random

    // Field weights
    var gravity: Vec3 = new Vec3(0, 0, -9.8);
    var gravityFactor: FastFloat = 1.0; // weight_gravity
	var textureFactor: FastFloat = 1.0; // weight_texture

	// Textures
	var textureSlots: Map<String, Dynamic> = [];

    // Armory props
    var autoStart: Bool = true; // auto_start
	var localCoords: Bool = false; // local_coords
    var loop: Bool = false; // loop

    // Internal logic
    var owner: MeshObject;
    var lifetimeSeconds: FastFloat = 0.0;
    var spawnRate: FastFloat = 0.0;
	var spawnFactor: Int = 1;
    var spawnedParticles: Int = 0;
	var particleScale: FastFloat = 1.0;
	var loopAnim: TAnim;
	var spawnTime: FastFloat = 0;

	// Tween scaling
	var scaleElementsCount: Int = 0;
	var scaleRampSizeFactor: FastFloat = 0;
	var tweenScaleSizeFactor: FastFloat = 0;
	var rampPositions: Array<FastFloat> = [];
	var rampColors: Array<FastFloat> = [];

	// Optimization
	var particlePool: Array<Object> = [];

    public function new(sceneName: String, pref: TParticleReference, mo: MeshObject) {
        Data.getParticle(sceneName, pref.particle, function (b: ParticleData) {
            data = b;
            r = data.raw;
			owner = mo;

			frameRate = r.fps;
			type = r.type;
            count = r.count;
            frameStart = r.frame_start;
            frameEnd = r.frame_end;
            lifetime = r.lifetime;
            lifetimeRandom = r.lifetime_random;
            emitFrom = r.emit_from;

			rotation = r.use_rotations;
			orientationAxis = r.rotation_mode;
			rotationRandom = r.rotation_factor_random;
			phase = r.phase_factor;
			phaseRandom = r.phase_factor_random;
			dynamicRotation = r.use_dynamic_rotation;

            instanceObject = r.instance_object;

            scale = r.particle_size;
            scaleRandom = r.size_random;

			velocity = new Vec3(r.object_align_factor[0], r.object_align_factor[1], r.object_align_factor[2]).mult(frameRate / baseFrameRate).mult(1 / scale);
            velocityRandom = r.factor_random * (frameRate / baseFrameRate);

            if (Scene.active.raw.gravity != null) {
                gravity = new Vec3(Scene.active.raw.gravity[0], Scene.active.raw.gravity[1], Scene.active.raw.gravity[2]).mult(frameRate / baseFrameRate).mult(1 / scale);
            }
            gravityFactor = r.weight_gravity * (frameRate / baseFrameRate);
			textureFactor = r.weight_texture;

			for (slot in Reflect.fields(r.texture_slots)) {
				textureSlots[slot] = Reflect.field(r.texture_slots, slot);
			}

            autoStart = r.auto_start;
			localCoords = r.local_coords;
            loop = r.loop;

            spawnRate = ((frameEnd - frameStart) / count) / frameRate;
            lifetimeSeconds = lifetime / frameRate;

			scaleElementsCount = getRampElementsLength();
			scaleRampSizeFactor = getRampSizeFactor();

			for (i in 0...count) addToPool();

			switch (type) {
				case 0: // Emission
					loopAnim = {
						tick: function () {
							spawnTime += Time.delta;
							var expected: Int = Math.floor(spawnTime / spawnRate);
							while (spawnedParticles < expected && spawnedParticles < count) {
								spawnParticle();
								spawnedParticles++;
							}
						},
						target: null,
						props: null,
						duration: lifetimeSeconds,
						done: function () {
							if (loop) start();
						}
					}

					if (autoStart) start();
				case 1: // Hair
					// HACK: wait for a few miliseconds until owner's world transform is properly set
					Tween.timer(0.05, function () {
						for (i in 0...count) spawnParticle();
					});
				default:
			}
		});
    }

    public function start() {
		if (type != 0) return;
		spawnTime = 0;
		spawnedParticles = 0;
		Tween.to(loopAnim);
    }

	// TODO
	public function pause() {

	}

	// TODO
	public function resume() {

	}

    public function stop() {
		if (type != 0) return;
		spawnTime = 0;
        spawnedParticles = 0;
		Tween.stop(loopAnim);
    }

	function addToPool() {
		Scene.active.spawnObject(instanceObject, localCoords ? owner : null, function (o: Object) {
			o.visible = false;
			particlePool.push(o);
		});
	}

	function getFreeParticle(): Object {
		for (particle in particlePool) {
			if (!particle.visible) {
				particle.visible = true;
				return particle;
			}
		}
		return null;
	}

	function releaseParticle(o: Object) {
		o.visible = false;
		o.transform.loc = new Vec4();
		o.transform.rot = new Quat();
		o.transform.scale = new Vec4(1, 1, 1, 1);
	}

    function spawnParticle() {
		var o: Object = getFreeParticle();
		if (o == null) {
			addToPool();
			o = getFreeParticle();
		}

		owner.transform.buildMatrix();

		var objectPos: Vec4 = new Vec4();
		var objectRot: Quat = new Quat();
		var objectScale: Vec4 = new Vec4();
		owner.transform.world.decompose(objectPos, objectRot, objectScale);

		o.visible = true;

		var normFactor: FastFloat = 1 / 32767;
		var scalePos: FastFloat = owner.data.scalePos;
		var scalePosParticle: FastFloat = cast(o, MeshObject).data.scalePos;
		var scaleFactor: Vec4  = new Vec4().setFrom(owner.transform.scale);
		scaleFactor.mult(scalePos / (scale * scalePosParticle));

		// TODO: add all properties from Blender's UI
		switch (emitFrom) {
			case 0: // Vertices
				var pa: TVertexArray = owner.data.geom.positions;
				var i: Int = Std.int(Math.random() * (pa.values.length / pa.size));
				var loc: Vec4 = new Vec4(pa.values[i * pa.size] * normFactor * scaleFactor.x, pa.values[i * pa.size + 1] * normFactor * scaleFactor.y, pa.values[i * pa.size + 2] * normFactor * scaleFactor.z, 1);

				if (!localCoords) loc.add(objectPos);
				o.transform.loc.setFrom(loc);
			case 1: // Faces
				var positions: Int16Array = owner.data.geom.positions.values;
				var ia: Uint32Array = owner.data.geom.indices[Std.random(owner.data.geom.indices.length)];
				var faceIndex: Int = Std.random(Std.int(ia.length / 3));

				var i0 = ia[faceIndex * 3 + 0];
				var i1 = ia[faceIndex * 3 + 1];
				var i2 = ia[faceIndex * 3 + 2];

				var v0: Vec3 = new Vec3(positions[i0 * 4], positions[i0 * 4 + 1], positions[i0 * 4 + 2]);
				var v1: Vec3 = new Vec3(positions[i1 * 4], positions[i1 * 4 + 1], positions[i1 * 4 + 2]);
				var v2: Vec3 = new Vec3(positions[i2 * 4], positions[i2 * 4 + 1], positions[i2 * 4 + 2]);

				var pos: Vec3 = randomPointInTriangle(v0, v1, v2);
				var loc: Vec4 = new Vec4(pos.x * scaleFactor.x, pos.y * scaleFactor.y, pos.z * scaleFactor.z, 1).mult(normFactor);

				if (!localCoords) loc.add(objectPos);
				o.transform.loc.setFrom(loc);
			case 2: // Volume
				var scaleFactorVolume: Vec4 = new Vec4().setFrom(owner.transform.dim);
				scaleFactorVolume.mult(0.5 / (scale * scalePosParticle));
				var loc: Vec4 = new Vec4((Math.random() * 2.0 - 1.0) * scaleFactorVolume.x, (Math.random() * 2.0 - 1.0) * scaleFactorVolume.y, (Math.random() * 2.0 - 1.0) * scaleFactorVolume.z, 1);

				if (!localCoords) loc.add(objectPos);
				o.transform.loc.setFrom(loc);
		}

		particleScale = 1 - scaleRandom * Math.random();
		var localFactor: Vec3 = localCoords ? new Vec3(objectScale.x, objectScale.y, objectScale.z) : new Vec3(1, 1, 1);
		var sc: Vec4 = new Vec4(o.transform.scale.x / localFactor.x, o.transform.scale.y / localFactor.y, o.transform.scale.z / localFactor.z, 1.0).mult(scale).mult(particleScale);
		var randomLifetime: FastFloat = lifetimeSeconds * (1 - Math.random() * lifetimeRandom);

		if (scaleElementsCount != 0) {
			tweenScaleSizeFactor = getRampSizeFactor();
			rampPositions = getRampPositions();
			rampColors = getRampColors();
			o.transform.scale.setFrom(sc.mult(rampColors[0]));
			if (type == 0) tweenParticleScale(o, randomLifetime);
		} else {
			o.transform.scale.setFrom(sc);
		}
		o.transform.buildMatrix();

		switch (type) {
			case 0: // Emission
				var randomX: FastFloat = (Math.random() * 2 / (scale * particleScale) - 1 / (scale * particleScale)) * velocityRandom;
				var randomY: FastFloat = (Math.random() * 2 / (scale * particleScale) - 1 / (scale * particleScale)) * velocityRandom;
				var randomZ: FastFloat = (Math.random() * 2 / (scale * particleScale) - 1 / (scale * particleScale)) * velocityRandom;
				var g: Vec3 = new Vec3();

				var rotatedVelocity: Vec4 = new Vec4(velocity.x + randomX, velocity.y + randomY, velocity.z + randomZ, 1);
				if (!localCoords) rotatedVelocity.applyQuat(objectRot);

				var randQuat: Quat;
				var phaseQuat: Quat;

				if (rotation) {
					// Rotation phase and randomness. Wrap values between -1 and 1.
					randQuat = new Quat().fromEuler((Math.random() * 2 - 1) * Math.PI * rotationRandom, (Math.random() * 2 - 1) * Math.PI * rotationRandom, (Math.random() * 2 - 1) * Math.PI * rotationRandom);
					var phaseRand: FastFloat = (Math.random() * 2 - 1) * phaseRandom;
					var phaseValue: FastFloat = phase + phaseRand;
					while (phaseValue > 1) phaseValue -= 2;
					while (phaseValue < -1) phaseValue += 2;
					var dirQuat: Quat = new Quat();
					phaseQuat = new Quat().fromEuler(0, phaseValue * Math.PI, 0);

					switch (orientationAxis) {
						case 0: // None
							o.transform.rotate(new Vec4(0, 0, 1, 1), -Math.PI * 0.5);
						case 3: // Velocity/Hair
							setVelocityHair(o, rotatedVelocity, randQuat, phaseQuat);
						case 4: // Global X
							o.transform.rot.fromEuler(0, 0, -Math.PI * 0.5).mult(phaseQuat).mult(randQuat);
						case 5: // Global Y
							o.transform.rot.fromEuler(0, 0, 0).mult(phaseQuat).mult(randQuat);
						case 6: // Global Z
							o.transform.rot.fromEuler(0, -Math.PI * 0.5, -Math.PI * 0.5).mult(phaseQuat).mult(randQuat);
						case 7: // Object X
							o.transform.rot.setFrom(objectRot);
							dirQuat.fromEuler(0, 0, -Math.PI * 0.5);
							o.transform.rot.mult(dirQuat).mult(phaseQuat).mult(randQuat);
						case 8: // Object Y
							o.transform.rot.setFrom(objectRot);
							o.transform.rot.mult(phaseQuat).mult(randQuat);
						case 9: // Object Z
							o.transform.rot.setFrom(objectRot);
							dirQuat.fromEuler(0, -Math.PI * 0.5, 0).mult(new Quat().fromEuler(0, 0, -Math.PI * 0.5));
							o.transform.rot.mult(dirQuat).mult(phaseQuat).mult(randQuat);
						default:
					}
				} else {
					o.transform.rotate(new Vec4(0, 0, 1, 1), -Math.PI * 0.5);
				}

				Tween.to({
					tick: function () {
						g.add(gravity.clone()).mult(Time.delta * gravityFactor);
						rotatedVelocity.add(new Vec4(g.x, g.y, g.z, 1));
						o.transform.translate(rotatedVelocity.x * Time.delta, rotatedVelocity.y * Time.delta, rotatedVelocity.z * Time.delta);
						if (rotation && dynamicRotation && orientationAxis == 3) setVelocityHair(o, rotatedVelocity, randQuat, phaseQuat);
						o.transform.buildMatrix();
					},
					target: null,
					props: null,
					duration: randomLifetime,
					done: function () {
						releaseParticle(o);
					}
				});
			case 1: // Hair
				var oLoc: Vec4 = localCoords ? o.transform.loc : o.transform.world.getLoc();
				var ownerLoc: Vec4 = localCoords ? new Vec4() : owner.transform.world.getLoc();

				var dir: Vec4 = new Vec4().setFrom(oLoc).sub(ownerLoc).normalize();
				var yaw: FastFloat = Math.atan2(-dir.x, dir.y);
				var pitch: FastFloat = Math.asin(dir.z);
				var targetRot: Quat = new Quat().fromEuler(pitch, 0, yaw);

				o.transform.rot.setFrom(targetRot);
		}
		o.transform.buildMatrix();
    }

	function setVelocityHair(object: Object, velocity: Vec4, randQuat: Quat, phaseQuat: Quat) {
		var dir: Vec4 = velocity.clone().normalize();
		var yaw: FastFloat = Math.atan2(-dir.x, dir.y);
		var pitch: FastFloat = Math.asin(dir.z);
		var targetRot: Quat = new Quat().fromEuler(pitch, 0, yaw);

		targetRot.mult(randQuat);
		object.transform.rot.setFrom(targetRot.mult(phaseQuat));
	}

	function tweenParticleScale(object: Object, lifetime: FastFloat, ?ease = null) {
		var anims: Array<TAnim> = [];
		var duration: FastFloat = rampPositions.length > 1 ? rampPositions[0] : 1 - rampPositions[0];

		for (i in 0...scaleElementsCount) {
			if (i > 0) {
				duration = (rampPositions[i] - rampPositions[i - 1]) * lifetime;
			}
			if (duration <= 0) continue;
			final scaleValue: FastFloat = scale * (particleScale * (1 - scaleRampSizeFactor) + rampColors[i] * scaleRampSizeFactor);

			anims.push({
				tick: function () {
					object.transform.buildMatrix();
				},
				target: object.transform.scale,
				props: {
					x: scaleValue,
					y: scaleValue,
					z: scaleValue
				},
				duration: duration,
				done: function () {
					if (anims.length > 1) {
						Tween.to(anims[1]);
						anims.shift();
					}
				}
			});
		}

		Tween.timer(rampPositions[0], function () {
			Tween.to(anims[0]);
		});
	}

	function getRampSizeFactor(): FastFloat {
		// Just using the first slot for now: 1 texture slot
		// TODO: use all available slots ?
		for (slot in textureSlots.keys()) {
			if (textureSlots[slot].use_map_size) return textureSlots[slot].size_factor * textureFactor;
		}
		return 0;
	}

	function getRampElementsLength(): Int {
		for (slot in textureSlots.keys()) {
			if (textureSlots[slot].texture.use_color_ramp) {
				return textureSlots[slot].texture.color_ramp.elements.length;
			}
		}
		return 0;
	}

	function getRampPositions(): Array<FastFloat> {
		// Just using the first slot for now: 1 texture slot
		// TODO: use all available slots ?
		for (slot in textureSlots.keys()) {
			if (textureSlots[slot].texture.use_color_ramp) {
				var positions: Array<FastFloat> = [];
				for (i in 0...textureSlots[slot].texture.color_ramp.elements.length) {
					positions.push(textureSlots[slot].texture.color_ramp.elements[i].position);
				}
				return positions;
			}
		}
		return [];
	}

	function getRampColors(): Array<FastFloat> {
		// Just using the first slot for now: 1 texture slot
		// TODO: use all available slots ?
		for (slot in textureSlots.keys()) {
			if (textureSlots[slot].texture.use_color_ramp) {
				var colors: Array<FastFloat> = [];
				for (i in 0...textureSlots[slot].texture.color_ramp.elements.length) {
					colors.push(textureSlots[slot].texture.color_ramp.elements[i].color.b); // Just need R, G or B for black and white images. Using B as it can be interpreted as V with HSV
				}
				return colors;
			}
		}
		return [];
	}

	public function remove() {
		for (particle in particlePool) particle.remove();
	}

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
