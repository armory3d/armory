package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class SetVelocityNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var linear: Vec4 = inputs[2].get();
		var linearFactor: Vec4 = inputs[3].get();
		var angular: Vec4 = inputs[4].get();
		var angularFactor: Vec4 = inputs[5].get();

		if (object == null || linear == null || linearFactor == null || angular == null || angularFactor == null) return;

#if arm_physics
		var rb: RigidBody = object.getTrait(RigidBody);
		rb.activate();
		rb.setLinearVelocity(linear.x, linear.y, linear.z);
		rb.setLinearFactor(linearFactor.x, linearFactor.y, linearFactor.z);
		rb.setAngularVelocity(angular.x, angular.y, angular.z);
		rb.setAngularFactor(angularFactor.x, angularFactor.y, angularFactor.z);
#end

		runOutput(0);
	}
}
