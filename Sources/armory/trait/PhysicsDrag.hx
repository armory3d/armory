package armory.trait;

import iron.Trait;
import iron.system.Input;
import armory.trait.internal.RigidBody;
import armory.trait.internal.PhysicsWorld;
#if WITH_PHYSICS
import haxebullet.Bullet;
#end

class PhysicsDrag extends Trait {

#if (!WITH_PHYSICS)
	public function new() { super(); }
#else

	var physics:PhysicsWorld;

	var pickConstraint:BtGeneric6DofConstraintPointer = null;
	var pickDist:Float;
	var pickedBody:RigidBody = null;

	var rayFrom:BtVector3Pointer;
	var rayTo:BtVector3Pointer;

	public function new() {
		super();

		notifyOnInit(init);
	}

	function init() {
		physics = armory.trait.internal.PhysicsWorld.active;
		notifyOnUpdate(update);
	}

	function update() {
		if (pickedBody != null) {
			pickedBody.activate();
		}

		if (Input.started) {
			var b = physics.pickClosest(Input.x, Input.y);

			if (b != null && b.mass > 0 && !b.body.ptr.isKinematicObject() && b.object.getTrait(PhysicsDrag) != null) {

				setRays();
				pickedBody = b;

				#if js
				var pickPos:BtVector3 = physics.rayCallback.get_m_hitPointWorld();
				#elseif cpp
				var pickPos:BtVector3 = physics.rayCallback.value.m_hitPointWorld;
				#end
				
				// var ct = b.object.transform.matrix;
				// var inv = iron.math.Mat4.identity();
				// inv.getInverse(ct);
				// var localPivotVec = new iron.math.Vec4(pickPos.x(), pickPos.y(), pickPos.z());
				// localPivotVec.applyMat4(inv);
				// var localPivot:BtVector3 = BtVector3.create(localPivotVec.x, localPivotVec.y, localPivotVec.z);

                var ct = b.body.ptr.getCenterOfMassTransform();
                var inv = ct.inverse();
				
				#if js
                var localPivot:BtVector3 = inv.mulVec(pickPos);
				#elseif cpp
                var localPivot:BtVector3 = untyped __cpp__("inv.value * pickPos.value"); // Operator overload
                #end

                var tr = BtTransform.create();
                tr.value.setIdentity();
                tr.value.setOrigin(localPivot);

                pickConstraint = BtGeneric6DofConstraint.create(b.body.value, tr.value, false);
                
				pickConstraint.value.setLinearLowerLimit(BtVector3.create(0, 0, 0).value);
                pickConstraint.value.setLinearUpperLimit(BtVector3.create(0, 0, 0).value);
                pickConstraint.value.setAngularLowerLimit(BtVector3.create(-10, -10, -10).value);
                pickConstraint.value.setAngularUpperLimit(BtVector3.create(10, 10, 10).value);

                physics.world.ptr.addConstraint(pickConstraint, false);

                /*pickConstraint.value.setParam(4, 0.8, 0);
                pickConstraint.value.setParam(4, 0.8, 1);
                pickConstraint.value.setParam(4, 0.8, 2);
                pickConstraint.value.setParam(4, 0.8, 3);
                pickConstraint.value.setParam(4, 0.8, 4);
                pickConstraint.value.setParam(4, 0.8, 5);

                pickConstraint.value.setParam(1, 0.1, 0);
                pickConstraint.value.setParam(1, 0.1, 1);
                pickConstraint.value.setParam(1, 0.1, 2);
                pickConstraint.value.setParam(1, 0.1, 3);
                pickConstraint.value.setParam(1, 0.1, 4);
                pickConstraint.value.setParam(1, 0.1, 5);*/

                var v = BtVector3.create(pickPos.x() - rayFrom.value.x(),
                						 pickPos.y() - rayFrom.value.y(),
                						 pickPos.z() - rayFrom.value.z());

                pickDist = v.value.length();

                Input.occupied = true;
			}
		}

		else if (Input.released) {

			if (pickConstraint != null) {
				physics.world.ptr.removeConstraint(pickConstraint);
				pickConstraint = null;
				pickedBody = null;
		    }

		    Input.occupied = false;
		}

		else if (Input.touch) {

		    if (pickConstraint != null) {
				
		    	setRays();

		        // Keep it at the same picking distance
		        var btRayTo = BtVector3.create(rayTo.value.x(), rayTo.value.y(), rayTo.value.z());
		        var btRayFrom = BtVector3.create(rayFrom.value.x(), rayFrom.value.y(), rayFrom.value.z());

		        var dir = BtVector3.create(btRayTo.value.x() - btRayFrom.value.x(),
		        						   btRayTo.value.y() - btRayFrom.value.y(),
		        						   btRayTo.value.z() - btRayFrom.value.z());

		        var bt = dir.value.normalize();
		        bt.setX(bt.x() * pickDist);
		        bt.setY(bt.y() * pickDist);
		        bt.setZ(bt.z() * pickDist);
				
		        var newPivotB = BtVector3.create(btRayFrom.value.x() + bt.x(),
		        								 btRayFrom.value.y() + bt.y(),
		        								 btRayFrom.value.z() + bt.z());

				#if js
		        pickConstraint.value.getFrameOffsetA().setOrigin(newPivotB.value);
				#elseif cpp
		        pickConstraint.value.setFrameOffsetAOrigin(newPivotB.value);
				#end
		    }
		}
	}

	inline function setRays() {
		rayFrom = physics.getRayFrom();
		rayTo = physics.getRayTo(Input.x, Input.y);
	}
#end
}
