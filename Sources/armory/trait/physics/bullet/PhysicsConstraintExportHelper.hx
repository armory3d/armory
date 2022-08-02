package armory.trait.physics.bullet;

import iron.Scene;
import iron.object.Object;
#if arm_bullet

/**
 * A helper trait to add physics constraints when exporting via Blender. 
 * This trait will be automatically removed once the constraint is added. Note that this trait
 * uses object names instead of object reference.
 **/
class PhysicsConstraintExportHelper extends iron.Trait {

	var body1: String;
	var body2: String;
	var type: Int;
	var disableCollisions: Bool;
	var breakingThreshold: Float;
	var limits: Array<Float>;
	var constraintAdded: Bool = false;
	var relativeConstraint: Bool = false;

	public function new(body1: String, body2: String, type: Int, disableCollisions: Bool, breakingThreshold: Float, relatieConstraint: Bool = false, limits: Array<Float> = null) {
		super();

		this.body1 = body1;
		this.body2 = body2;
		this.type = type;
		this.disableCollisions = disableCollisions;
		this.breakingThreshold = breakingThreshold;
		this.relativeConstraint = relatieConstraint;
		this.limits = limits;
		notifyOnInit(init);
		notifyOnUpdate(update);
	}

	function init() {
		var target1; 
		var target2;

		if(relativeConstraint) {

			target1 = object.parent.getChild(body1);
			target2 = object.parent.getChild(body2);
		}
		else {
			
			target1 = Scene.active.getChild(body1);
			target2 = Scene.active.getChild(body2);
		}
		object.addTrait(new PhysicsConstraint(target1, target2, type, disableCollisions, breakingThreshold, limits));
		constraintAdded = true;
	}

	function update() {
		if(constraintAdded) this.remove();
	}
}

#end
