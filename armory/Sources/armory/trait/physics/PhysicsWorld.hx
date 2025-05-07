package armory.trait.physics;

#if (!arm_physics)

class Hit {
}

class PhysicsWorld extends iron.Trait {
	public function new() { super(); }
}

#else

	#if arm_bullet

	typedef PhysicsWorld = armory.trait.physics.bullet.PhysicsWorld;
	typedef Hit = armory.trait.physics.bullet.PhysicsWorld.Hit;

	#else

	typedef PhysicsWorld = armory.trait.physics.oimo.PhysicsWorld;
	typedef Hit = armory.trait.physics.oimo.PhysicsWorld.Hit;

	#end

#end
