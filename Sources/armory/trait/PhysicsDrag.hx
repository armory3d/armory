package armory.trait;

import iron.Trait;
import iron.system.Input;
import iron.math.Vec4;
import iron.math.RayCaster;
import armory.trait.physics.RigidBody;
import armory.trait.physics.PhysicsWorld;
#if arm_bullet
import haxebullet.Bullet;
#end

class PhysicsDrag extends Trait {

#if (!arm_bullet)
	public function new() { super(); }
#else

	static var physics:PhysicsWorld = null;

	var pickConstraint:BtGeneric6DofConstraintPointer = null;
	var pickDist:Float;
	var pickedBody:RigidBody = null;

	var rayFrom:BtVector3;
	var rayTo:BtVector3;

	public function new() {
		super();

		notifyOnInit(init);
	}

	function init() {
		if (physics == null) physics = armory.trait.physics.PhysicsWorld.active;
		notifyOnUpdate(update);
	}

	function update() {
		if (pickedBody != null) {
			pickedBody.activate();
		}

		var mouse = Input.getMouse();
		if (mouse.started()) {
			var b = physics.pickClosest(mouse.x, mouse.y);

			if (b != null && b.mass > 0 && !b.body.isKinematicObject() && b.object.getTrait(PhysicsDrag) != null) {

				setRays();
				pickedBody = b;

				var hit = physics.hitPointWorld;
				var pickPos:BtVector3 = BtVector3.create(hit.x, hit.y, hit.z);
				
				// var ct = b.object.transform.world;
				// var inv = iron.math.Mat4.identity();
				// inv.getInverse(ct);
				// var localPivotVec = new iron.math.Vec4(pickPos.x(), pickPos.y(), pickPos.z());
				// localPivotVec.applyMat4(inv);
				// var localPivot:BtVector3 = BtVector3.create(localPivotVec.x, localPivotVec.y, localPivotVec.z);

				var ct = b.body.getCenterOfMassTransform();
				return; // TODO: .inverse() missing in new ammo
				var inv = ct.inverse();
				
				#if js
				var localPivot:BtVector3 = inv.mulVec(pickPos);
				#elseif cpp
				var localPivot:BtVector3 = untyped __cpp__("inv * pickPos"); // Operator overload
				#end

				var tr = BtTransform.create();
				tr.setIdentity();
				tr.setOrigin(localPivot);

				pickConstraint = BtGeneric6DofConstraint.create(b.body, tr, false);
				
				pickConstraint.setLinearLowerLimit(BtVector3.create(0, 0, 0));
				pickConstraint.setLinearUpperLimit(BtVector3.create(0, 0, 0));
				pickConstraint.setAngularLowerLimit(BtVector3.create(-10, -10, -10));
				pickConstraint.setAngularUpperLimit(BtVector3.create(10, 10, 10));

				physics.world.addConstraint(pickConstraint, false);

				/*pickConstraint.setParam(4, 0.8, 0);
				pickConstraint.setParam(4, 0.8, 1);
				pickConstraint.setParam(4, 0.8, 2);
				pickConstraint.setParam(4, 0.8, 3);
				pickConstraint.setParam(4, 0.8, 4);
				pickConstraint.setParam(4, 0.8, 5);

				pickConstraint.setParam(1, 0.1, 0);
				pickConstraint.setParam(1, 0.1, 1);
				pickConstraint.setParam(1, 0.1, 2);
				pickConstraint.setParam(1, 0.1, 3);
				pickConstraint.setParam(1, 0.1, 4);
				pickConstraint.setParam(1, 0.1, 5);*/

				var v = BtVector3.create(pickPos.x() - rayFrom.x(),
										 pickPos.y() - rayFrom.y(),
										 pickPos.z() - rayFrom.z());

				pickDist = v.length();

				Input.occupied = true;
			}
		}

		else if (mouse.released()) {

			if (pickConstraint != null) {
				physics.world.removeConstraint(pickConstraint);
				pickConstraint = null;
				pickedBody = null;
			}

			Input.occupied = false;
		}

		else if (mouse.down()) {

			if (pickConstraint != null) {
				
				setRays();

				// Keep it at the same picking distance
				var btRayTo = BtVector3.create(rayTo.x(), rayTo.y(), rayTo.z());
				var btRayFrom = BtVector3.create(rayFrom.x(), rayFrom.y(), rayFrom.z());

				var dir = BtVector3.create(btRayTo.x() - btRayFrom.x(),
										   btRayTo.y() - btRayFrom.y(),
										   btRayTo.z() - btRayFrom.z());

				var bt = dir.normalize();
				bt.setX(bt.x() * pickDist);
				bt.setY(bt.y() * pickDist);
				bt.setZ(bt.z() * pickDist);
				
				var newPivotB = BtVector3.create(btRayFrom.x() + bt.x(),
												 btRayFrom.y() + bt.y(),
												 btRayFrom.z() + bt.z());

				#if js
				pickConstraint.getFrameOffsetA().setOrigin(newPivotB);
				#elseif cpp
				pickConstraint.setFrameOffsetAOrigin(newPivotB);
				#end
			}
		}
	}

	inline function setRays() {
		var mouse = Input.getMouse();
		var camera = iron.Scene.active.camera;
		
		var v = camera.transform.world.getLoc();
		rayFrom = BtVector3.create(v.x, v.y, v.z);
		var start = new Vec4();
		var end = new Vec4();
		RayCaster.getDirection(start, end, mouse.x, mouse.y, camera);
		rayTo = BtVector3.create(end.x, end.y, end.z);
	}
#end
}
