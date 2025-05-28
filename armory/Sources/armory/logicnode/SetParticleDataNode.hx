package armory.logicnode;

import iron.object.Object;

class SetParticleDataNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_particles
		var object: Object = inputs[1].get();
		var slot: Int = inputs[2].get();

		if (object == null) return;

		var mo = cast(object, iron.object.MeshObject);

		var psys = mo.particleSystems != null ? mo.particleSystems[slot] : 
			mo.particleOwner != null && mo.particleOwner.particleSystems != null ? mo.particleOwner.particleSystems[slot] : null;		if (psys == null) return;

		switch (property0) {
			case 'Particle Size':
				psys.r.particle_size = inputs[3].get();
			case 'Frame Start':
				psys.r.frame_start = inputs[3].get();
				psys.animtime = (psys.r.frame_end - psys.r.frame_start) / psys.frameRate;
				psys.spawnRate = ((psys.r.frame_end - psys.r.frame_start) / psys.count) / psys.frameRate;
			case 'Frame End':
				psys.r.frame_end = inputs[3].get();
				psys.animtime = (psys.r.frame_end - psys.r.frame_start) / psys.frameRate;
				psys.spawnRate = ((psys.r.frame_end - psys.r.frame_start) / psys.count) / psys.frameRate;
			case 'Lifetime':
				psys.lifetime = inputs[3].get() / psys.frameRate;
			case 'Lifetime Random':
				psys.r.lifetime_random = inputs[3].get();
			case 'Emit From':
				var emit_from: Int = inputs[3].get();
				if (emit_from == 0 || emit_from == 1 || emit_from == 2) {
					psys.r.emit_from = emit_from;
					psys.setupGeomGpu(mo.particleChildren != null ? mo.particleChildren[slot] : cast(iron.Scene.active.getChild(psys.data.raw.instance_object), iron.object.MeshObject), mo);
				}
			case 'Auto Start':
				psys.r.auto_start = inputs[3].get(); 
			case 'Is Unique':
				psys.r.is_unique = inputs[3].get();
			case 'Loop':
				psys.r.loop = inputs[3].get();
			case 'Velocity':
				var vel: iron.math.Vec3 = inputs[3].get();
				psys.alignx = vel.x;
				psys.aligny = vel.y;
				psys.alignz = vel.z;
			case 'Velocity Random':
				psys.r.factor_random = inputs[3].get();
			case 'Weight Gravity':
				psys.r.weight_gravity = inputs[3].get();
				if (iron.Scene.active.raw.gravity != null) {
					psys.gx = iron.Scene.active.raw.gravity[0] * psys.r.weight_gravity;
					psys.gy = iron.Scene.active.raw.gravity[1] * psys.r.weight_gravity;
					psys.gz = iron.Scene.active.raw.gravity[2] * psys.r.weight_gravity;
				}
				else {
					psys.gx = 0;
					psys.gy = 0;
					psys.gz = -9.81 * psys.r.weight_gravity;
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
