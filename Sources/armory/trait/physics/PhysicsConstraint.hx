package armory.trait.physics;

#if (!arm_physics)

import iron.Trait;

class PhysicsConstraint extends Trait { public function new() { super(); } }

#else

	#if arm_bullet

	typedef PhysicsConstraint = armory.trait.physics.bullet.PhysicsConstraint;

	#else

	typedef PhysicsConstraint = armory.trait.physics.oimo.PhysicsConstraint;

	#end

#end
