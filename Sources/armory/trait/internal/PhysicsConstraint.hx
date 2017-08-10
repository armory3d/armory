package armory.trait.internal;

import iron.math.Vec4;
import iron.math.Mat4;
import iron.Trait;
import iron.object.MeshObject;
import iron.data.MeshData;
import iron.data.SceneFormat;
#if arm_physics
import armory.trait.internal.RigidBody;
import armory.trait.internal.PhysicsWorld;
import haxebullet.Bullet;
#end

class PhysicsConstraint extends Trait {
#if (!arm_physics)
	public function new() { super(); }
#else

	var body1:String;
	var body2:String;

	public function new(body1:String, body2:String) {
		super();

		this.body1 = body1;
		this.body2 = body2;

		Scene.active.notifyOnInit(function() {
			notifyOnInit(init);
		});
	}

	function init() {
		
		var physics = PhysicsWorld.active;

		var target1 = iron.Scene.active.getChild(body1);
		var target2 = iron.Scene.active.getChild(body2);

		if (target1 == null || target2 == null) return;

		var rb1:RigidBody = target1.getTrait(RigidBody);
		var rb2:RigidBody = target2.getTrait(RigidBody);

		if (rb1 != null && rb1.ready && rb2 != null && rb2.ready) {
			#if js // TODO
			var constraint = BtHingeConstraint.create(rb1.body, rb2.body,
				BtVector3.create(0, 0.0, -2.0),
				BtVector3.create(0, 0.0, 2.0),
				BtVector3.create(0, 0, 2.0),
				BtVector3.create(0, 0, 2.0));
			// constraint.setLimit(0.0, Math.PI / 2.0);
			physics.world.addConstraint(constraint, true);
			#end
			return;
		}

		// Rigid body not initialized yet
		notifyOnInit(init);
	}

#end
}
