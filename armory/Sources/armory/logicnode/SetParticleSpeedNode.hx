package armory.logicnode;

import iron.object.Object;

class SetParticleSpeedNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_gpu_particles
		var object: Object = inputs[1].get();
		var slot: Int = inputs[2].get();
		var speed: Float = inputs[3].get();

		if (object == null) return;

		var mo = cast(object, iron.object.MeshObject);
	
		var psys = mo.particleSystems != null ? mo.particleSystems[slot] : 
			mo.particleOwner != null && mo.particleOwner.particleSystems != null ? mo.particleOwner.particleSystems[slot] : null;
			
		if (psys == null) return;

		psys.speed = speed;

		#end

		runOutput(0);
	}
}
