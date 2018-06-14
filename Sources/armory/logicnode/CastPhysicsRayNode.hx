package armory.logicnode;

import iron.math.Vec4;

#if arm_physics
import haxebullet.Bullet;
#end

class CastPhysicsRayNode extends LogicNode {

	var v = new Vec4();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var vfrom:Vec4 = inputs[0].get();
		var vto:Vec4 = inputs[1].get();

		if (vfrom == null || vto == null) return null;

#if arm_physics
		var physics = armory.trait.physics.PhysicsWorld.active;
		var rb = physics.rayCast(vfrom, vto);

		if (from == 0) { // Object
			if (rb != null) return rb.object;
		}
		else { // Hit
			var hitPointWorld:Vec4 = rb != null ? physics.hitPointWorld : null;
			v.set(hitPointWorld.x, hitPointWorld.y, hitPointWorld.z);
			return v;
		}
#end
		return null;
	}
}
