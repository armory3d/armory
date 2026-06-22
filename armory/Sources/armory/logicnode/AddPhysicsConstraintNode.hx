package armory.logicnode;

import iron.object.Object;

#if arm_bullet
import armory.trait.physics.PhysicsConstraint;
import armory.trait.physics.bullet.PhysicsConstraint.ConstraintType;
#elseif arm_oimo
// TODO
#end

class AddPhysicsConstraintNode extends LogicNode {

	public var property0: String;//Type
	public var object: Object;
	public var rb1: Object;
	public var rb2: Object;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var pivotObject: Object = inputs[1].get();
		rb1 = inputs[2].get();
		rb2 = inputs[3].get();

		if (pivotObject == null || rb1 == null || rb2 == null) return;

#if arm_bullet

		var disableCollisions: Bool = inputs[4].get();
		var breakable: Bool = inputs[5].get();
		var breakingThreshold: Float = inputs[6].get();
		var type: ConstraintType = 0;

		var con: PhysicsConstraint = pivotObject.getTrait(PhysicsConstraint);
		if (con == null) {
			switch (property0) {
				case "Fixed": type = Fixed;
				case "Point": type = Point;
				case "Hinge": type = Hinge;
				case "Slider": type = Slider;
				case "Piston": type = Piston;
				case "Generic Spring": type = Generic;
			}

			if (!breakable) breakingThreshold = 0.0;

			if (type != Generic) {

				con = new PhysicsConstraint(rb1, rb2, type, disableCollisions, breakingThreshold);

				switch (type) {
					case Hinge:
						var setLimit: Bool = inputs[7].get();
						var low: Float = inputs[8].get();
						var up: Float = inputs[9].get();
						con.setHingeConstraintLimits(setLimit, low, up);

					case Slider:
						var setLimit: Bool = inputs[7].get();
						var low: Float = inputs[8].get();
						var up: Float = inputs[9].get();
						con.setSliderConstraintLimits(setLimit, low, up);

					case Piston:
						var setLinLimit: Bool = inputs[7].get();
						var linLow: Float = inputs[8].get();
						var linUp: Float = inputs[9].get();
						var setAngLimit: Bool = inputs[10].get();
						var angLow: Float = inputs[11].get();
						var angUp: Float = inputs[12].get();
						con.setPistonConstraintLimits(setLinLimit, linLow, linUp, setAngLimit, angLow, angUp);

					default:
				}
			}
			else {
				var spring: Bool = false;
				var prop: PhysicsConstraintNode;

				for (inp in 7...inputs.length) {
					prop = inputs[inp].get();
					if (prop == null) continue;
					if (prop.isSpring) {
						spring = true;
						break;
					}
				}

				if (spring) {
					con = new PhysicsConstraint(rb1, rb2, GenericSpring, disableCollisions, breakingThreshold);
				}
				else {
					con = new PhysicsConstraint(rb1, rb2, Generic, disableCollisions, breakingThreshold);
				}

				for (inp in 7...inputs.length) {
					prop = inputs[inp].get();
					if (prop == null) continue;

					if (prop.isSpring) {
						con.setSpringParams(prop.isSpring, prop.value1, prop.value2, prop.axis, prop.isAngular);
					}
					else {
						con.setGenericConstraintLimits(true, prop.value1, prop.value2, prop.axis, prop.isAngular);
					}
				}
			}
			pivotObject.addTrait(con);
		}
#elseif arm_oimo
// TODO
#end
		runOutput(0);
	}
}
