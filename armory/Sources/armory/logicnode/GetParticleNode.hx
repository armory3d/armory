package armory.logicnode;

import iron.object.Object;

class GetParticleNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();

		if (object == null) return null;

	#if arm_particles

		var mo = cast(object, iron.object.MeshObject);
	
		switch (from) {
			case 0:
				var names: Array<String> = [];
				if (mo.particleSystems != null)
					for (psys in mo.particleSystems)
						names.push(psys.r.name);
				return names;
			case 1:
				return mo.particleSystems != null ? mo.particleSystems.length : 0;
			case 2:
				return mo.render_emitter;
			default: 
				null;
		}
	#end

		return null;
	}
}
