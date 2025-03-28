package armory.trait.physics;

#if (!arm_physics)

class PhysicsHook extends iron.Trait { public function new() { super(); } }

#else

	#if arm_bullet

	typedef PhysicsHook = armory.trait.physics.bullet.PhysicsHook;

	#else

	typedef PhysicsHook = armory.trait.physics.oimo.PhysicsHook;

	#end

#end
