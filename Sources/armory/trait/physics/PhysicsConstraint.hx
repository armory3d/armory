package armory.trait.physics;

#if (!arm_physics)

class PhysicsConstraint extends iron.Trait { public function new() { super(); } }

#else

	#if arm_bullet

	typedef PhysicsConstraint = armory.trait.physics.bullet.PhysicsConstraint;

	#else

	typedef PhysicsConstraint = armory.trait.physics.oimo.PhysicsConstraint;

	#end

#end
