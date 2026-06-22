package armory.trait;

import iron.math.Vec4;
import iron.system.Input;
import armory.trait.physics.RigidBody;
import armory.trait.physics.KinematicCharacterController;

/**
	Simple script to scale an object around using the keyboard.
	All axis can be scaled at once using the Z and X keys.
	Individual axis can be scaled using YU(x), HJ(y), NM(z).
	Can be used for testing and debuging.
**/
class SimpleScaleObject extends iron.Trait {

	@prop
	var speed: Float = 0.1;

	var keyboard: Keyboard;
	var rb: RigidBody;
	var character: KinematicCharacterController;

	public function new() {
		super();

		notifyOnInit(function() {
			rb = object.getTrait(RigidBody);
			character = object.getTrait(KinematicCharacterController);
			keyboard = Input.getKeyboard();
		});

		notifyOnUpdate(function() {
			var scale = new Vec4(0, 0, 0);

			if (keyboard.down("y")) {
				scale.x += speed;
			}

			if (keyboard.down("u")) {
				scale.x -= speed;
			}

			if (keyboard.down("h")) {
				scale.y += speed;
			}

			if (keyboard.down("j")) {
				scale.y -= speed;
			}

			if (keyboard.down("n")) {
				scale.z += speed;
			}

			if (keyboard.down("m")) {
				scale.z -= speed;
			}

			if (keyboard.down("z")) {
				scale.set(speed, speed, speed);
			}

			if (keyboard.down("x")) {
				scale.set(-speed, -speed, -speed);
			}

			if (!scale.equals(new Vec4(0, 0, 0))) {
				scaleObject(scale);
			}
		});
	}

	function scaleObject(vec: Vec4){
		var s = object.transform.scale;
		if (rb != null) {
			#if arm_physics
			rb.transform.scale.set(s.x + vec.x, s.y + vec.y, s.z + vec.z);
			rb.syncTransform();
			#end
		}
		else if (character != null) {
			#if arm_physics
			character.transform.scale.set(s.x + vec.x, s.y + vec.y, s.z + vec.z);
			character.syncTransform();
			#end
		}
		else {
			object.transform.scale.set(s.x + vec.x, s.y + vec.y, s.z + vec.z);
			object.transform.buildMatrix();
		}
	}
}
