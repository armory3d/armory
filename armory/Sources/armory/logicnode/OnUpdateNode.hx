package armory.logicnode;

import armory.trait.physics.PhysicsWorld;

class OnUpdateNode extends LogicNode {

	public var property0: String; // Update, Late Update, Physics Pre-Update

	public function new(tree: LogicTree) {
		super(tree);
		tree.notifyOnInit(init);
	}

	function init() {
		switch (property0) {
		case "Fixed Update": tree.notifyOnFixedUpdate(update);
		case "Late Update": tree.notifyOnLateUpdate(update);
		#if arm_physics
		case "Physics Pre-Update": PhysicsWorld.active.notifyOnPreUpdate(update);
		#end
		default: tree.notifyOnUpdate(update); /* Update */
		}
	}

	function update() {
		runOutput(0);
	}
}
