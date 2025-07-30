package armory.trait.physics;

#if (!arm_physics)

class RigidBody extends iron.Trait { public function new() { super(); } }
@:enum abstract Shape(Int) from Int to Int { }

#else

	#if arm_bullet

	typedef RigidBody = armory.trait.physics.bullet.RigidBody;
	typedef Shape = armory.trait.physics.bullet.RigidBody.Shape;

	#else

	typedef RigidBody = armory.trait.physics.oimo.RigidBody;
	typedef Shape = armory.trait.physics.oimo.RigidBody.Shape;

	#end

#end
