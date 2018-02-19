package armory.trait.physics.bullet;

#if arm_bullet

import armory.trait.physics.RigidBody;
import armory.trait.physics.PhysicsWorld;
import haxebullet.Bullet;

class PhysicsConstraint extends iron.Trait {

	var body1:String;
	var body2:String;
	var type:String;
	var disableCollisions:Bool;
	var breakingThreshold:Float;
	var limits:Array<Float>;
	var con:BtTypedConstraintPointer = null;

	public function new(body1:String, body2:String, type:String, disableCollisions:Bool, breakingThreshold:Float, limits:Array<Float> = null) {
		super();
		this.body1 = body1;
		this.body2 = body2;
		this.type = type;
		this.disableCollisions = disableCollisions;
		this.breakingThreshold = breakingThreshold;
		this.limits = limits;
		notifyOnInit(init);
	}

	function init() {
		var physics = PhysicsWorld.active;
		var target1 = iron.Scene.active.getChild(body1);
		var target2 = iron.Scene.active.getChild(body2);
		if (target1 == null || target2 == null) return;

		var rb1:RigidBody = target1.getTrait(RigidBody);
		var rb2:RigidBody = target2.getTrait(RigidBody);

		if (rb1 != null && rb1.ready && rb2 != null && rb2.ready) {

			var t = object.transform;
			var t1 = target1.transform;
			var t2 = target2.transform;
			var p1 = BtVector3.create(t.worldx() - t1.worldx(), t.worldy() - t1.worldy(), t.worldz() - t1.worldz());
			var p2 = BtVector3.create(t.worldx() - t2.worldx(), t.worldy() - t2.worldy(), t.worldz() - t2.worldz());
			var tr1 = BtTransform.create();
			tr1.setIdentity();
			tr1.setOrigin(p1);
			var tr2 = BtTransform.create();
			tr2.setIdentity();
			tr2.setOrigin(p2);

			
			if (type == "GENERIC" || type == "FIXED" || type == "POINT") {
				var c = BtGeneric6DofConstraint.create2(rb1.body, rb2.body, tr1, tr2, false);
				if (type == "POINT") {
					c.setLinearLowerLimit(BtVector3.create(0, 0, 0));
					c.setLinearUpperLimit(BtVector3.create(0, 0, 0));
				}
				else if (type == "FIXED") {
					c.setLinearLowerLimit(BtVector3.create(0, 0, 0));
					c.setLinearUpperLimit(BtVector3.create(0, 0, 0));
					c.setAngularLowerLimit(BtVector3.create(0, 0, 0));
					c.setAngularUpperLimit(BtVector3.create(0, 0, 0));
				}
				else { // GENERIC
					// limit_x:Bool = limits[0] > 0.0;
					c.setLinearLowerLimit(BtVector3.create(limits[1], limits[4], limits[7]));
					c.setLinearUpperLimit(BtVector3.create(limits[2], limits[5], limits[8]));
					c.setAngularLowerLimit(BtVector3.create(limits[10], limits[13], limits[16]));
					c.setAngularUpperLimit(BtVector3.create(limits[11], limits[14], limits[17]));
				}
				con = cast c;
			}
			else if (type == "HINGE") {
				var axis = BtVector3.create(0, 0, 1.0);
				var c = BtHingeConstraint.create(rb1.body, rb2.body, p2, p1, axis, axis);
				con = cast c;
			}
			// else if (type == "SLIDER") {}
			// else if (type == "PISTON") {}

			if (breakingThreshold > 0) con.setBreakingImpulseThreshold(breakingThreshold);

			physics.world.addConstraint(con, disableCollisions);
		}
		else notifyOnInit(init); // Rigid body not initialized yet
	}
}

#end
