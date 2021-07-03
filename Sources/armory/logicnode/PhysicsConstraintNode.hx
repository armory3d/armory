package armory.logicnode;

#if arm_physics
import armory.trait.physics.bullet.PhysicsConstraint.ConstraintAxis;
#end

class PhysicsConstraintNode extends LogicNode {

	public var property0: String; //Linear or Angular
	public var property1: String; //Axis
	public var property2: Bool; //Is a spring
	public var value1: Float; //Lower limit or Spring Stiffness
	public var value2: Float; //Upper limit or Spring Damping
	public var isAngular: Bool;
	public var axis: ConstraintAxis;
	public var isSpring: Bool;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): PhysicsConstraintNode {
		value1 = inputs[0].get();
		value2 = inputs[1].get();

		isAngular = property0 != "Linear";
		isSpring = property2;

		switch (property1){
			case "X": axis = X;
			case "Y": axis = Y;
			case "Z": axis = Z;
		}

		return this;
	}
}
