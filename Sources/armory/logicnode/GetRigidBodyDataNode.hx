package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

class GetRigidBodyDataNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();

		if (object == null) return null;

#if arm_physics
		var rb = object.getTrait(RigidBody);

		return switch (from) {
			case 0:
				rb == null ? return false : return true;
			case 1:
				rb.group;
			case 2:
				rb.mask;
			case 3:
				rb.animated;
			case 4:
				rb.staticObj;
			case 5:
				rb.angularDamping;
			case 6:
				rb.linearDamping;
			case 7:
				rb.friction;
			case 8:
				rb.mass;
			//case 9: ; // collision shape
			//case 10: ; // activation state
			//case 11: ; // is gravity enabled
			//case 12: ; // angular factor
			//case 13: ; // linear factor
			default: 
				null;
		}
#end

		return null;
	}
}
