package armory.logicnode;

import armory.trait.physics.PhysicsWorld;

@:access(iron.Trait)
class OnInitNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
		tree.notifyOnInit(init);
	}

	function init() {
		#if arm_physics
		var noPhysics = PhysicsWorld.active == null || PhysicsWorld.active._lateUpdate == null;
		noPhysics ? run(this) : PhysicsWorld.active.notifyOnPreUpdate(physics_init);
		#else
		run(this);
		#end
	}

	#if arm_physics
	function physics_init() {
		PhysicsWorld.active.removePreUpdate(physics_init);
		run(this);
	}
	#end
}
