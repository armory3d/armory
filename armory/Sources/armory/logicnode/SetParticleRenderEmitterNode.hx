package armory.logicnode;

import iron.object.Object;

class SetParticleRenderEmitterNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_particles
		var object: Object = inputs[1].get();

		if (object == null) return;

		cast(object, iron.object.MeshObject).render_emitter = inputs[2].get();

		#end

		runOutput(0);
	}
}
