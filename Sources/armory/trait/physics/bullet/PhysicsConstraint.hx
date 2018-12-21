package armory.trait.physics.bullet;

#if arm_bullet

import armory.trait.physics.RigidBody;
import armory.trait.physics.PhysicsWorld;

class PhysicsConstraint extends iron.Trait {

	var body1:String;
	var body2:String;
	var type:String;
	var disableCollisions:Bool;
	var breakingThreshold:Float;
	var limits:Array<Float>;
	var con:bullet.Bt.TypedConstraint = null;

	static var nullvec = true;
	static var vec1:bullet.Bt.Vector3;
	static var vec2:bullet.Bt.Vector3;
	static var vec3:bullet.Bt.Vector3;
	static var trans1:bullet.Bt.Transform;
	static var trans2:bullet.Bt.Transform;

	public function new(body1:String, body2:String, type:String, disableCollisions:Bool, breakingThreshold:Float, limits:Array<Float> = null) {
		super();

		if (nullvec) {
			nullvec = false;
			vec1 = new bullet.Bt.Vector3(0, 0, 0);
			vec2 = new bullet.Bt.Vector3(0, 0, 0);
			vec3 = new bullet.Bt.Vector3(0, 0, 0);
			trans1 = new bullet.Bt.Transform();
			trans2 = new bullet.Bt.Transform();
		}
		
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
			trans1.setIdentity();
			vec1.setX(t.worldx() - t1.worldx());
			vec1.setY(t.worldy() - t1.worldy());
			vec1.setZ(t.worldz() - t1.worldz());
			trans1.setOrigin(vec1);
			trans2.setIdentity();
			vec2.setX(t.worldx() - t2.worldx());
			vec2.setY(t.worldy() - t2.worldy());
			vec2.setZ(t.worldz() - t2.worldz());
			trans2.setOrigin(vec2);
			
			if (type == "GENERIC" || type == "FIXED" || type == "POINT") {
				var c = bullet.Bt.Generic6DofConstraint.new2(rb1.body, rb2.body, trans1, trans2, false);
				if (type == "POINT") {
					vec1.setX(0);
					vec1.setY(0);
					vec1.setZ(0);
					c.setLinearLowerLimit(vec1);
					c.setLinearUpperLimit(vec1);
				}
				else if (type == "FIXED") {
					vec1.setX(0);
					vec1.setY(0);
					vec1.setZ(0);
					c.setLinearLowerLimit(vec1);
					c.setLinearUpperLimit(vec1);
					c.setAngularLowerLimit(vec1);
					c.setAngularUpperLimit(vec1);
				}
				else { // GENERIC
					// limit_x:Bool = limits[0] > 0.0;
					vec1.setX(limits[1]);
					vec1.setY(limits[4]);
					vec1.setZ(limits[7]);
					c.setLinearLowerLimit(vec1);
					vec1.setX(limits[2]);
					vec1.setY(limits[5]);
					vec1.setZ(limits[8]);
					c.setLinearUpperLimit(vec1);
					vec1.setX(limits[10]);
					vec1.setY(limits[13]);
					vec1.setZ(limits[16]);
					c.setAngularLowerLimit(vec1);
					vec1.setX(limits[11]);
					vec1.setY(limits[14]);
					vec1.setZ(limits[17]);
					c.setAngularUpperLimit(vec1);
				}
				con = cast c;
			}
			else if (type == "HINGE") {
				var axis = vec3;
				axis.setX(0);
				axis.setY(0);
				axis.setZ(1);
				var c = new bullet.Bt.HingeConstraint(rb1.body, rb2.body, vec2, vec1, axis, axis);
				con = cast c;
			}
			// else if (type == "SLIDER") {}
			// else if (type == "PISTON") {}

			if (breakingThreshold > 0) con.setBreakingImpulseThreshold(breakingThreshold);

			physics.world.addConstraint(con, disableCollisions);
		}
		else notifyOnInit(init); // Rigid body not initialized yet
	}

	public function removeFromWorld() {
		#if js
		bullet.Bt.Ammo.destroy(con);
		#end
	}
}

#end
