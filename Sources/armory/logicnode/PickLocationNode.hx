package armory.logicnode;

import armory.object.Object;
import armory.math.Vec4;

class PickLocationNode extends Node {

	var loc = new Vec4();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object:Object = inputs[0].get();
		var coords:Vec4 = inputs[1].get();
		
		if (object == null) object = tree.object;

#if arm_physics
		var physics = armory.trait.internal.PhysicsWorld.active;
		var b = physics.pickClosest(coords.x, coords.y);
		var rb = object.getTrait(armory.trait.internal.RigidBody);

		if (rb != null && b == rb) {
			var p:haxebullet.Bullet.BtVector3 = physics.hitPointWorld;
			loc.set(p.x(), p.y(), p.z());
			return loc;
		}
#end
		return null;
	}
}
