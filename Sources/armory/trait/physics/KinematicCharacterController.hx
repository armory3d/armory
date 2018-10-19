package armory.trait.physics;

#if (!arm_physics)

import iron.Trait;

class KinematicCharacterController extends Trait { public function new() { super(); } }

#else

	#if arm_bullet

	typedef KinematicCharacterController = armory.trait.physics.bullet.KinematicCharacterController;

	#end

#end
