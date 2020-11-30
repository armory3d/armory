package armory.trait.physics.bullet;

import iron.Scene;
import iron.object.Object;
#if arm_bullet
import Math;
import iron.math.Quat;
import armory.trait.physics.RigidBody;
import armory.trait.physics.PhysicsWorld;


class PhysicsConstraint extends iron.Trait {

	static var nextId:Int = 0;
	public var id:Int = 0;

	var physics: PhysicsWorld;
	var body1: Object;
	var body2: Object;
	var type: ConstraintType;
	public var disableCollisions: Bool;
	var breakingThreshold: Float;
	var limits: Array<Float>;
	public var con: bullet.Bt.TypedConstraint = null;

	static var nullvec = true;
	static var vec1: bullet.Bt.Vector3;
	static var vec2: bullet.Bt.Vector3;
	static var vec3: bullet.Bt.Vector3;
	static var trans1: bullet.Bt.Transform;
	static var trans2: bullet.Bt.Transform;
	static var transt: bullet.Bt.Transform;

	public function new(body1: Object, body2: Object, type: ConstraintType, disableCollisions: Bool, breakingThreshold: Float, limits: Array<Float> = null) {
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

		physics = PhysicsWorld.active;
		var target1 = body1;
		var target2 = body2;

		if (target1 == null || target2 == null) return;//no objects selected

		var rb1: RigidBody = target1.getTrait(RigidBody);
		var rb2: RigidBody = target2.getTrait(RigidBody);

		if (rb1 != null && rb1.ready && rb2 != null && rb2.ready) {//Check if rigid bodies are ready

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

			trans1.setRotation(new bullet.Bt.Quaternion(t.rot.x, t.rot.y, t.rot.z, t.rot.w));
			trans2.setRotation(new bullet.Bt.Quaternion(t.rot.x, t.rot.y, t.rot.z, t.rot.w));

			if (type == Generic || type == Fixed) {
				#if hl
				var c = new bullet.Bt.Generic6DofConstraint(rb1.body, rb2.body, trans1, trans2, false);
				#else
				var c = bullet.Bt.Generic6DofConstraint.new2(rb1.body, rb2.body, trans1, trans2, false);
				#end
				if (type == Fixed) {
					vec1.setX(0);
					vec1.setY(0);
					vec1.setZ(0);
					c.setLinearLowerLimit(vec1);
					c.setLinearUpperLimit(vec1);
					c.setAngularLowerLimit(vec1);
					c.setAngularUpperLimit(vec1);
				}
				else if (type == ConstraintType.Generic) {
					if (limits[0] == 0) {
						limits[1] = 1.0;
						limits[2] = -1.0;
					}
					if (limits[3] == 0) {
						limits[4] = 1.0;
						limits[5] = -1.0;
					}
					if (limits[6] == 0) {
						limits[7] = 1.0;
						limits[8] = -1.0;
					}
					if (limits[9] == 0) {
						limits[10] = 1.0;
						limits[11] = -1.0;
					}
					if (limits[12] == 0) {
						limits[13] = 1.0;
						limits[14] = -1.0;
					}
					if (limits[15] == 0) {
						limits[16] = 1.0;
						limits[17] = -1.0;
					}
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
			else if (type == ConstraintType.GenericSpring){
				var c = new bullet.Bt.Generic6DofSpringConstraint(rb1.body, rb2.body, trans1, trans2, false);

				if (limits[0] == 0) {
					limits[1] = 1.0;
					limits[2] = -1.0;
				}
				if (limits[3] == 0) {
					limits[4] = 1.0;
					limits[5] = -1.0;
				}
				if (limits[6] == 0) {
					limits[7] = 1.0;
					limits[8] = -1.0;
				}
				if (limits[9] == 0) {
					limits[10] = 1.0;
					limits[11] = -1.0;
				}
				if (limits[12] == 0) {
					limits[13] = 1.0;
					limits[14] = -1.0;
				}
				if (limits[15] == 0) {
					limits[16] = 1.0;
					limits[17] = -1.0;
				}
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
				if (limits[18] != 0) {
					c.enableSpring(0, true);
					c.setStiffness(0, limits[19]);
					c.setDamping(0, limits[20]);
				}
				else {
					c.enableSpring(0, false);
				}
				if (limits[21] != 0) {
					c.enableSpring(1, true);
					c.setStiffness(1, limits[22]);
					c.setDamping(1, limits[23]);
				}
				else {
					c.enableSpring(1, false);
				}
				if (limits[24] != 0) {
					c.enableSpring(2, true);
					c.setStiffness(2, limits[25]);
					c.setDamping(2, limits[26]);
				}
				else {
					c.enableSpring(2, false);
				}
				if (limits[27] != 0) {
					c.enableSpring(3, true);
					c.setStiffness(3, limits[28]);
					c.setDamping(3, limits[29]);
				}
				else {
					c.enableSpring(3, false);
				}
				if (limits[30] != 0) {
					c.enableSpring(4, true);
					c.setStiffness(4, limits[31]);
					c.setDamping(4, limits[32]);
				}
				else {
					c.enableSpring(4, false);
				}
				if (limits[33] != 0) {
					c.enableSpring(5, true);
					c.setStiffness(5, limits[34]);
					c.setDamping(5, limits[35]);
				}
				else {
					c.enableSpring(5, false);
				}
				con = cast c;

			}
			else if (type == ConstraintType.Point){
				var c = new bullet.Bt.Point2PointConstraint(rb1.body, rb2.body, vec1, vec2);
				con = cast c;
			}
			else if (type == ConstraintType.Hinge) {
				var axis = vec3;
				var _softness: Float = 0.9;
				var _biasFactor: Float = 0.3;
				var _relaxationFactor: Float = 1.0;

				axis.setX(t.up().x);
				axis.setY(t.up().y);
				axis.setZ(t.up().z);

				var c = new bullet.Bt.HingeConstraint(rb1.body, rb2.body, vec1, vec2, axis, axis, false);

				if (limits[0] != 0) {
					c.setLimit(limits[1], limits[2], _softness, _biasFactor, _relaxationFactor);
				}

				con = cast c;
			}
			else if (type == ConstraintType.Slider) {
				var c = new bullet.Bt.SliderConstraint(rb1.body, rb2.body, trans1, trans2, true);

				if (limits[0] != 0) {
					c.setLowerLinLimit(limits[1]);
					c.setUpperLinLimit(limits[2]);
				}

				con = cast c;
			}
			else if (type == ConstraintType.Piston) {
				var c = new bullet.Bt.SliderConstraint(rb1.body, rb2.body, trans1, trans2, true);

				if (limits[0] != 0) {
					c.setLowerLinLimit(limits[1]);
					c.setUpperLinLimit(limits[2]);
				}
				if (limits[3] != 0) {
					c.setLowerAngLimit(limits[4]);
					c.setUpperAngLimit(limits[5]);
				}
				else {
					c.setLowerAngLimit(1);
					c.setUpperAngLimit(-1);

				}
				con = cast c;
			}

			if (breakingThreshold > 0) con.setBreakingImpulseThreshold(breakingThreshold);

			physics.addPhysicsConstraint(this);
			
			id = nextId;
			nextId++;


			notifyOnRemove(removeFromWorld);
		}
		else this.remove(); // Rigid body not initialized yet. Remove trait without adding constraint
	}

	public function removeFromWorld() {
		physics.removePhysicsConstraint(this);
	}

	public function delete() {
		#if js
		bullet.Bt.Ammo.destroy(con);
		#else
		con.delete();
		#end
	}

	
}

@:enum abstract ConstraintType(Int) from Int to Int {
	var Fixed = 0;
	var Point = 1;
	var Hinge = 2;
	var Slider = 3;
	var Piston = 4;
	var Generic = 5;
	var GenericSpring = 6;
	var Motor = 7;
}

#end
