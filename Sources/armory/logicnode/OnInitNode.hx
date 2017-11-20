package armory.logicnode;

import armory.trait.physics.PhysicsWorld;

class OnInitNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);

		#if arm_physics
		PhysicsWorld.active.notifyOnPreUpdate(init);
		#else
		tree.notifyOnInit(init);
		#end
	}

	function init() {
		#if arm_physics
		PhysicsWorld.active.removePreUpdate(init);
		#end
		run();
	}
}
