package armory.trait.physics;

#if (!arm_physics)

class PhysicsConstraint extends iron.Trait { public function new() { super(); } }
@:enum abstract ConstraintAxis(Int) from Int to Int { }

#else

	#if arm_bullet

	typedef PhysicsConstraint = armory.trait.physics.bullet.PhysicsConstraint;
	typedef ConstraintAxis = armory.trait.physics.bullet.PhysicsConstraint.ConstraintAxis;

	#else

	typedef PhysicsConstraint = armory.trait.physics.oimo.PhysicsConstraint;
	typedef ConstraintAxis = armory.trait.physics.oimo.PhysicsConstraint.ConstraintAxis;

	#end

#end
