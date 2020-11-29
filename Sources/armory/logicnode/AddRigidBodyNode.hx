package armory.logicnode;

#if arm_physics
import armory.trait.physics.bullet.RigidBody.Shape;
#end
import iron.object.Object;
import armory.trait.physics.RigidBody;

class AddRigidBodyNode extends LogicNode {

	public var property0: String;//Shape
	public var property1: String;//Advanced
	public var object: Object;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		object = inputs[1].get();
		var mass: Float = inputs[2].get();
		var active: Bool = inputs[3].get();
		var animated: Bool = inputs[4].get();
		var trigger: Bool = inputs[5].get();
		var friction: Float = inputs[6].get();
		var bounciness: Float = inputs[7].get();
		var ccd: Bool = inputs[8].get();

		var margin: Bool = false;
		var marginLen: Float = 0.0;
		var linDamp: Float = 0.0;
		var angDamp: Float = 0.0;
		var useDeactiv: Bool = false;
		var linearVelThreshold: Float = 0.0;
		var angVelThreshold: Float = 0.0;
		var group: Int = 1;
		var mask: Int = 1;

		var shape: Shape = 1;

		if(property1 == 'true')
		{
			margin = inputs[9].get();
			marginLen = inputs[10].get();
			linDamp = inputs[11].get();
			angDamp = inputs[12].get();
			useDeactiv = inputs[13].get();
			linearVelThreshold = inputs[14].get();
			angVelThreshold = inputs[15].get();
			group = inputs[16].get();
			mask = inputs[17].get();

		}


		if (object == null) return;

#if arm_physics
		var rb: RigidBody = object.getTrait(RigidBody);
		if((group < 0) || (group > 32)) group = 1; //Limiting max groups to 32
		if((mask < 0) || (mask > 32)) mask = 1; //Limiting max masks to 32
		if(rb == null)
		{

			switch (property0){

				case 'Box':
					shape = Box;
				case 'Sphere':
					shape = Sphere;
				case 'Capsule':
					shape = Capsule;
				case 'Cone':
					shape = Cone;
				case 'Cylinder':
					shape = Cylinder;
				case 'Convex Hull':
					shape = ConvexHull;
				case 'Mesh':
					shape = Mesh;
			}

			rb = new RigidBody(shape, mass, friction, bounciness, group, mask);
			rb.animated = animated;
			rb.staticObj = ! active;
			rb.isTriggerObject(trigger);
			if(property1 == 'true')
			{
				rb.linearDamping = linDamp;
				rb.angularDamping = angDamp;
				if(margin) rb.collisionMargin = marginLen;
				if(useDeactiv) {
					rb.setDeactivation(true);
					rb.setDeactivationParams(linearVelThreshold, angVelThreshold, 0.0);
				}

			}

			object.addTrait(rb);
		}
#end

		runOutput(0);
	}

	override function get(from: Int): Object {
		return object;
	}
}
