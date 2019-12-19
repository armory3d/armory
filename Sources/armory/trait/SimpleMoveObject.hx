package armory.trait;

import iron.math.Vec4;
import iron.system.Input;
import armory.trait.physics.RigidBody;

/**
    Simple script to move an object around using the keyboard with WSAD+QE.
	Can be used for testing and debuging.
**/
class SimpleMoveObject extends iron.Trait {

	@prop
	var speed: Float = 0.1;

	var keyboard: Keyboard;
	var rb: RigidBody;

	public function new() {
		super();

		notifyOnInit(function() {
			rb = object.getTrait(RigidBody);
			keyboard = Input.getKeyboard();
		});

		notifyOnUpdate(function() {
			var move = new Vec4(0, 0, 0);

			if (keyboard.down("d")) {
				move.x += speed;
			}

			if (keyboard.down("a")) {
				move.x -= speed;
			}

			if (keyboard.down("w")) {
				move.y += speed;
			}

			if (keyboard.down("s")) {
				move.y -= speed;
			}

			if (keyboard.down("q")) {
				move.z += speed;
			}

			if (keyboard.down("e")) {
				move.z -= speed;
			}

			if (!move.equals(new Vec4(0, 0, 0))) {
				moveObject(move);
			}
		});
	}

	function moveObject(vec: Vec4){
		if (rb != null) {
			#if arm_physics
			rb.setLinearVelocity(0, 0, 0);
			rb.setAngularVelocity(0, 0, 0);
			rb.transform.translate(vec.x, vec.y, vec.z);
			rb.syncTransform();
			#end
		}
		else {
			object.transform.translate(vec.x, vec.y, vec.z);
		}
	}
}
