package armory.logicnode;

import iron.object.Object;

class RemoveParticleFromObjectNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_particles
		var object: Object = inputs[1].get();

		if (object == null) return;

		var mo = cast(object, iron.object.MeshObject);

		if (mo.particleSystems == null) return;

		if (property0 == 'All'){
			mo.particleSystems = null;
			for (c in mo.particleChildren) c.remove();
			mo.particleChildren = null;
			mo.particleOwner = null;
			mo.render_emitter = true;
		} 
		else {
			//remuevo y quedan mas o remuevo solo 1 y queda en null???
			var slot: Int = -1;
			if (property0 == 'Name'){
				var name: String = inputs[2].get();
				for (i => psys in mo.particleSystems){
					trace(psys.r.name, psys.r.name == name, i);
					if (psys.r.name == name){ slot = i; break; }
				}
			} 
			else slot = inputs[2].get();
				
			if (mo.particleSystems.length > slot){
				for (i in slot+1...mo.particleSystems.length){
					var mi = cast(mo.particleChildren[i], iron.object.MeshObject);
					mi.particleIndex = mi.particleIndex - 1;
				}
				mo.particleSystems.splice(slot, 1);
				mo.particleChildren[slot].remove();
				mo.particleChildren.splice(slot, 1);
			}

			if (slot == 0){
				mo.particleSystems = null;
				mo.particleChildren = null;
				mo.particleOwner = null;
				mo.render_emitter = true;
			}

		}

		#end

		runOutput(0);
	}
}
