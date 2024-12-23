package armory.trait.physics;

#if (!arm_physics)

class PhysicsWorld extends iron.Trait { public function new() { super(); } }

#else

	#if arm_bullet

	typedef PhysicsWorld = armory.trait.physics.bullet.PhysicsWorld;

	#else

	typedef PhysicsWorld = armory.trait.physics.oimo.PhysicsWorld;

	#end

#end
