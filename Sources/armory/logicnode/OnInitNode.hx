package armory.logicnode;

import armory.trait.physics.PhysicsWorld;

class OnInitNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
		tree.notifyOnInit(init);
	}

	function init() {
		#if arm_physics
		PhysicsWorld.active == null ? run() : PhysicsWorld.active.notifyOnPreUpdate(physics_init);
		#else
		run();
		#end
	}

	#if arm_physics
	function physics_init() {
		PhysicsWorld.active.removePreUpdate(physics_init);
		run();
	}
	#end
}
