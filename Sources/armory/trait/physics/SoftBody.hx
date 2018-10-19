package armory.trait.physics;

#if (!arm_physics_soft)

import iron.Trait;

class SoftBody extends Trait { public function new() { super(); } }

#else

	#if arm_bullet

	typedef SoftBody = armory.trait.physics.bullet.SoftBody;

	#else

	typedef SoftBody = armory.trait.physics.oimo.SoftBody;

	#end

#end
