package armory.trait.physics;

#if (!arm_physics)

class RigidBody extends iron.Trait { public function new() { super(); } }

#else

	#if arm_bullet

	typedef RigidBody = armory.trait.physics.bullet.RigidBody;

	#else

	typedef RigidBody = armory.trait.physics.oimo.RigidBody;

	#end

#end
