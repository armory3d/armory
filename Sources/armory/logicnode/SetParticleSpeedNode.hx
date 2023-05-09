package armory.logicnode;

import iron.object.Object;

class SetParticleSpeedNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_particles
		var object: Object = inputs[1].get();
		var speed: Float = inputs[2].get();

		if (object == null) return;

		var mo = cast(object, iron.object.MeshObject);
		var psys = mo.particleSystems.length > 0 ? mo.particleSystems[0] : null;
		if (psys == null) mo.particleOwner.particleSystems[0];

		psys.speed = speed;

		runOutput(0);
		#end
	}
}
