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
				@:privateAccess psys.r.name;
			case 1:
				@:privateAccess psys.r.particle_size;
			case 2:
				@:privateAccess psys.r.frame_start;
			case 3:
				@:privateAccess psys.r.frame_end;
			case 4:
				@:privateAccess psys.lifetime;
			case 5:
				@:privateAccess psys.r.lifetime;
			case 6:
				@:privateAccess psys.r.emit_from;
			case 7:
				new iron.math.Vec3(@:privateAccess psys.alignx*2, @:privateAccess psys.aligny*2, @:privateAccess psys.alignz*2);
			case 8:
				@:privateAccess psys.r.factor_random;
			case 9:
				new iron.math.Vec3(@:privateAccess psys.gx, @:privateAccess psys.gy, @:privateAccess psys.gz);
			case 10:
				@:privateAccess psys.r.weight_gravity;
			case 11:
				psys.speed;
			case 12:
				@:privateAccess psys.time;
			case 13:
				@:privateAccess psys.lap;
			case 14:
				@:privateAccess psys.lapTime;
			case 15:
				@:privateAccess psys.count;
			default:
				null;
		}
	#end

		return null;
	}
}
