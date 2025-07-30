package armory.logicnode;

import iron.object.Object;

class SetParticleDataNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_gpu_particles
		var object: Object = inputs[1].get();
		var slot: Int = inputs[2].get();

		if (object == null) return;

		var mo = cast(object, iron.object.MeshObject);

		var psys = mo.particleSystems != null ? mo.particleSystems[slot] :
			mo.particleOwner != null && mo.particleOwner.particleSystems != null ? mo.particleOwner.particleSystems[slot] : null;		if (psys == null) return;

		switch (property0) {
			case 'Particle Size':
				@:privateAccess psys.r.particle_size = inputs[3].get();
			case 'Frame Start':
				@:privateAccess psys.r.frame_start = inputs[3].get();
				@:privateAccess psys.animtime = (@:privateAccess psys.r.frame_end - @:privateAccess psys.r.frame_start) / @:privateAccess psys.frameRate;
				@:privateAccess psys.spawnRate = ((@:privateAccess psys.r.frame_end - @:privateAccess psys.r.frame_start) / @:privateAccess psys.count) / @:privateAccess psys.frameRate;
			case 'Frame End':
				@:privateAccess psys.r.frame_end = inputs[3].get();
				@:privateAccess psys.animtime = (@:privateAccess psys.r.frame_end - @:privateAccess psys.r.frame_start) / @:privateAccess psys.frameRate;
				@:privateAccess psys.spawnRate = ((@:privateAccess psys.r.frame_end - @:privateAccess psys.r.frame_start) / @:privateAccess psys.count) / @:privateAccess psys.frameRate;
			case 'Lifetime':
				@:privateAccess psys.lifetime = inputs[3].get() / @:privateAccess psys.frameRate;
			case 'Lifetime Random':
				@:privateAccess psys.r.lifetime_random = inputs[3].get();
			case 'Emit From':
				var emit_from: Int = inputs[3].get();
				if (emit_from == 0 || emit_from == 1 || emit_from == 2) {
					@:privateAccess psys.r.emit_from = emit_from;
					@:privateAccess psys.setupGeomGpu(mo.particleChildren != null ? mo.particleChildren[slot] : cast(iron.Scene.active.getChild(@:privateAccess psys.data.raw.instance_object), iron.object.MeshObject), mo);
				}
			case 'Auto Start':
				@:privateAccess psys.r.auto_start = inputs[3].get();
			case 'Is Unique':
				@:privateAccess psys.r.is_unique = inputs[3].get();
			case 'Loop':
				@:privateAccess psys.r.loop = inputs[3].get();
			case 'Velocity':
				var vel: iron.math.Vec3 = inputs[3].get();
				@:privateAccess psys.alignx = vel.x;
				@:privateAccess psys.aligny = vel.y;
				@:privateAccess psys.alignz = vel.z;
			case 'Velocity Random':
				@:privateAccess psys.r.factor_random = inputs[3].get();
			case 'Weight Gravity':
				@:privateAccess psys.r.weight_gravity = inputs[3].get();
				if (iron.Scene.active.raw.gravity != null) {
					@:privateAccess psys.gx = iron.Scene.active.raw.gravity[0] * @:privateAccess psys.r.weight_gravity;
					@:privateAccess psys.gy = iron.Scene.active.raw.gravity[1] * @:privateAccess psys.r.weight_gravity;
					@:privateAccess psys.gz = iron.Scene.active.raw.gravity[2] * @:privateAccess psys.r.weight_gravity;
				}
				else {
					@:privateAccess psys.gx = 0;
					@:privateAccess psys.gy = 0;
					@:privateAccess psys.gz = -9.81 * @:privateAccess psys.r.weight_gravity;
				}
			case 'Speed':
				psys.speed = inputs[3].get();
			default:
				null;
		}

		#end

		runOutput(0);
	}
}
