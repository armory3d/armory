package armory.logicnode;

import iron.object.Object;

class GetParticleDataNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();
		var slot: Int = inputs[1].get();

		if (object == null) return null;

	#if arm_particles

		var mo = cast(object, iron.object.MeshObject);

		var psys = mo.particleSystems != null ? mo.particleSystems[slot] : 
			mo.particleOwner != null && mo.particleOwner.particleSystems != null ? mo.particleOwner.particleSystems[slot] : null;

		if (psys == null) return null;

		return switch (from) {
			case 0:
				psys.r.name;
			case 1:
				psys.r.particle_size;
			case 2:
				psys.r.frame_start;
			case 3:
				psys.r.frame_end;
			case 4:
				psys.lifetime;
			case 5:
				psys.r.lifetime;
			case 6:
				psys.r.emit_from;
			case 7:
				psys.r.auto_start;
			case 8:
				psys.r.is_unique;
			case 9:
				psys.r.loop;
			case 10:
				new iron.math.Vec3(psys.alignx*2, psys.aligny*2, psys.alignz*2);
			case 11:
				psys.r.factor_random;
			case 12:
				new iron.math.Vec3(psys.gx, psys.gy, psys.gz);
			case 13:
				psys.r.weight_gravity;
			case 14:
				psys.speed;
			case 15:
				psys.time;
			case 16:
				psys.lap;
			case 17:
				psys.lapTime;
			case 18:
				psys.count;
			default: 
				null;
		}
	#end

		return null;
	}
}
