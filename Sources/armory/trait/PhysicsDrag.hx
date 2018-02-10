package armory.trait;

import iron.Trait;
import iron.system.Input;
import iron.math.Vec4;
import iron.math.Mat4;
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

	var pickConstraint:BtGeneric6DofConstraintPointer = null;
	var pickDist:Float;
	var pickedBody:RigidBody = null;

	var rayFrom:BtVector3;
	var rayTo:BtVector3;

	static var v = new Vec4();
	static var m = Mat4.identity();
	static var first = true;

	public function new() {
		super();
		if (first) {
			first = false;
			notifyOnUpdate(update);
		}
	}

	function update() {
		var physics = PhysicsWorld.active;
		if (pickedBody != null) pickedBody.activate();

		var mouse = Input.getMouse();
		if (mouse.started()) {
			
			var b = physics.pickClosest(mouse.x, mouse.y);
			if (b != null && b.mass > 0 && !b.body.isKinematicObject() && b.object.getTrait(PhysicsDrag) != null) {

				setRays();
				pickedBody = b;

				m.getInverse(b.object.transform.world);
				var hit = physics.hitPointWorld;
				v.setFrom(hit);
				v.applymat4(m);
				var localPivot = BtVector3.create(v.x, v.y, v.z);
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

				pickDist = v.set(hit.x - rayFrom.x(), hit.y - rayFrom.y(), hit.z - rayFrom.z()).length();

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
				var dir = BtVector3.create(rayTo.x() - rayFrom.x(), rayTo.y() - rayFrom.y(), rayTo.z() - rayFrom.z());
				dir.normalize();
				dir.setX(dir.x() * pickDist);
				dir.setY(dir.y() * pickDist);
				dir.setZ(dir.z() * pickDist);
				var newPivotB = BtVector3.create(rayFrom.x() + dir.x(), rayFrom.y() + dir.y(), rayFrom.z() + dir.z());

				#if js
				pickConstraint.getFrameOffsetA().setOrigin(newPivotB);
				#elseif cpp
				pickConstraint.setFrameOffsetAOrigin(newPivotB);
				#end
			}
		}
	}

	static var start = new Vec4();
	static var end = new Vec4();
	inline function setRays() {
		var mouse = Input.getMouse();
		var camera = iron.Scene.active.camera;
		var v = camera.transform.world.getLoc();
		rayFrom = BtVector3.create(v.x, v.y, v.z);
		RayCaster.getDirection(start, end, mouse.x, mouse.y, camera);
		rayTo = BtVector3.create(end.x, end.y, end.z);
	}
#end
}
