package armory.logicnode;

import armory.math.Vec4;

class PickLocationNode extends Node {

	var loc = new Vec4();

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function get(from:Int):Dynamic {
		var object = inputs[0].get();
		var coords = inputs[1].get();
		
		if (object == null) object = trait.object;

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
