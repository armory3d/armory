package armory.logicnode;

import armory.trait.physics.PhysicsWorld;

@:access(iron.Trait)
class OnInitNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
		tree.notifyOnInit(init);
	}

	function init() {
		#if arm_physics
		var noPhysics = PhysicsWorld.active == null || PhysicsWorld.active._lateUpdate == null;
		noPhysics ? runOutput(0) : PhysicsWorld.active.notifyOnPreUpdate(physics_init);
		#else
		runOutput(0);
		#end
	}

	#if arm_physics
	function physics_init() {
		PhysicsWorld.active.removePreUpdate(physics_init);
		runOutput(0);
	}
	#end
}
