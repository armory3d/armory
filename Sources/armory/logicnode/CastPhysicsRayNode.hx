package armory.logicnode;

import armory.math.Vec4;

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

#if arm_physics
		var rayFrom = BtVector3.create(vfrom.x, vfrom.y, vfrom.z);
		var rayTo = BtVector3.create(vto.x, vto.y, vto.z);
		var physics = armory.trait.internal.PhysicsWorld.active;
		var rayCallback = ClosestRayResultCallback.create(rayFrom, rayTo);
		physics.world.rayTest(rayFrom, rayTo, rayCallback);

		if (rayCallback.hasHit()) {
			
			#if js
			
			if (from == 0)  { // Object
				var co = rayCallback.get_m_collisionObject();
				var body = untyped Ammo.btRigidBody.prototype.upcast(co);
				return physics.rbMap.get(untyped body.userIndex).object;
			}
			else { // Hit
				var hitPointWorld = rayCallback.get_m_hitPointWorld();
				return v.set(hitPointWorld.x(), hitPointWorld.y(), hitPointWorld.z());
			}

			#elseif cpp
			
			if (from == 0) { // Object
				return physics.rbMap.get(rayCallback.m_collisionObject.getUserIndex()).object;
			}
			else { // Hit
				var hitPointWorld = rayCallback.m_hitPointWorld;
				return v.set(hitPointWorld.x(), hitPointWorld.y(), hitPointWorld.z());
			}
			#end
		}
#end
		return null;
	}
}
