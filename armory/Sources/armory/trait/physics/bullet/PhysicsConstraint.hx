package armory.trait.physics.bullet;

import iron.math.Vec4;
import iron.Scene;
import iron.object.Object;
#if arm_bullet
import Math;
import iron.math.Quat;
import armory.trait.physics.RigidBody;
import armory.trait.physics.PhysicsWorld;

/**
 * A trait to add Bullet physics constraints
 **/
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

	/**
	 * Function to initialize physics constraint trait.
	  * 
	  * @param object Pivot object to which this constraint trait will be added. The constraint limits are applied along the local axes of this object. This object need not 
	  * be a Rigid Body. Typically an `Empty` object may be used. Moving/rotating/parenting this pivot object has no effect once the constraint trait is added. Removing
	  * the pivot object removes the constraint.
	  * 
	  * @param body1 First rigid body to be constrained. This rigid body may be constrained by other constraints.
	  * 
	  * @param body2 Second rigid body to be constrained. This rigid body may be constrained by other constraints.
	  * 
	  * @param type Type of the constraint.
	  * 
	  * @param disableCollisions Disable collisions between constrained objects.
	  * 
	  * @param breakingThreshold Break the constraint if stress on this constraint exceeds this value. Set to 0 to make un-breakable.
	  * 
	  * @param limits Constraint limits. This may be set before adding the trait to pivot object using the set limits functions.
	  * 
 	**/
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
		if(limits == null) limits = [for(i in 0...36) 0];
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

			var frameT = t.world.clone();//Transform of pivot in world space

			var frameInA = t1.world.clone();//Transform of rb1 in world space
			frameInA.getInverse(frameInA);//Inverse Transform of rb1 in world space
			frameT.multmat(frameInA);//Transform of pivot object in rb1 space
			frameInA = frameT.clone();//Frame In A

			frameT = t.world.clone();//Transform of pivot in world space

			var frameInB = t2.world.clone();//Transform of rb2 in world space
			frameInB.getInverse(frameInB);//Inverse Transform of rb2 in world space
			frameT.multmat(frameInB);//Transform of pivot object in rb2 space
			frameInB = frameT.clone();//Frame In B

			var loc = new Vec4();
			var rot = new Quat();
			var scl = new Vec4();

			frameInA.decompose(loc,rot,scl);
			trans1.setIdentity();
			vec1.setX(loc.x);
			vec1.setY(loc.y);
			vec1.setZ(loc.z);
			trans1.setOrigin(vec1);
			trans1.setRotation(new bullet.Bt.Quaternion(rot.x, rot.y, rot.z, rot.w));

			frameInB.decompose(loc,rot,scl);
			trans2.setIdentity();
			vec2.setX(loc.x);
			vec2.setY(loc.y);
			vec2.setZ(loc.z);
			trans2.setOrigin(vec2);
			trans2.setRotation(new bullet.Bt.Quaternion(rot.x, rot.y, rot.z, rot.w));

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

	/**
 	 * Function to set constraint limits when using Hinge constraint. May be used after initalizing this trait but before adding it
     * to the pivot object 
 	**/
	public function setHingeConstraintLimits(angLimit: Bool, lowerAngLimit: Float, upperAngLimit: Float) {
		
		angLimit? limits[0] = 1 : limits[0] = 0;

		limits[1] = lowerAngLimit * (Math.PI/ 180);
		limits[2] = upperAngLimit * (Math.PI/ 180);
	}

	/**
 	 * Function to set constraint limits when using Slider constraint. May be used after initalizing this trait but before adding it
     * to the pivot object 
 	**/
	public function setSliderConstraintLimits(linLimit: Bool, lowerLinLimit: Float, upperLinLimit: Float) {
		
		linLimit? limits[0] = 1 : limits[0] = 0;

		limits[1] = lowerLinLimit;
		limits[2] = upperLinLimit;
	}

	/**
 	 * Function to set constraint limits when using Piston constraint. May be used after initalizing this trait but before adding it
     * to the pivot object 
 	**/
	public function setPistonConstraintLimits(linLimit: Bool, lowerLinLimit: Float, upperLinLimit: Float, angLimit: Bool, lowerAngLimit: Float, upperAngLimit: Float) {
		
		linLimit? limits[0] = 1 : limits[0] = 0;

		limits[1] = lowerLinLimit;
		limits[2] = upperLinLimit;

		angLimit? limits[3] = 1 : limits[3] = 0;

		limits[4] = lowerAngLimit * (Math.PI/ 180);
		limits[5] = upperAngLimit * (Math.PI/ 180);
	}

	/**
 	 * Function to set customized constraint limits when using Generic/ Generic Spring constraint. May be used after initalizing this trait but before adding it
     * to the pivot object. Multiple constarints may be set by calling this function with different parameters.
 	**/
	public function setGenericConstraintLimits(setLimit: Bool = false, lowerLimit: Float = 1.0, upperLimit: Float = -1.0, axis: ConstraintAxis = X, isAngular: Bool = false) {

		var i = 0;
		var j = 0;
		var radian = (Math.PI/ 180);

		switch (axis){
			case X: 
				i = 0;
			case Y:
				i = 3;
			case Z:
				i = 6;
		}

		isAngular? j = 9 : j = 0;

		isAngular? radian = (Math.PI/ 180) : radian = 1;

		setLimit? limits[i + j] = 1 : 0;
		limits[i + j + 1] = lowerLimit * radian;
		limits[i + j + 2] = upperLimit * radian;

	}

	/**
 	 * Function to set customized spring parameters when using Generic/ Generic Spring constraint. May be used after initalizing this trait but before adding it
     * to the pivot object. Multiple parameters to different axes may be set by calling this function with different parameters.
 	**/
	public function setSpringParams(setSpring: Bool = false, stiffness: Float = 10.0, damping: Float = 0.5, axis: ConstraintAxis = X, isAngular: Bool = false) {

		var i = 0;
		var j = 0;

		switch (axis){
			case X: 
				i = 18;
			case Y:
				i = 21;
			case Z:
				i = 24;
		}

		isAngular? j =  9 : j = 0;

		setSpring? limits[i + j] = 1 : 0;
		limits[i + j + 1] = stiffness;
		limits[i + j + 2] = damping;

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

@:enum abstract ConstraintAxis(Int) from Int to Int {
	var X = 0;
	var Y = 1;
	var Z = 2;
}

#end
