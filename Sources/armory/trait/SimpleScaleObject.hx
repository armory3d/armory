package armory.trait;

import iron.math.Vec4;
import iron.system.Input;
import armory.trait.physics.RigidBody;

/**
	Simple script to scale an object around using the keyboard.
	All axis can be scaled at once using the up and down arrows.
	Individual axis can be scaled using YU(x), HJ(y), NM(z).
	Can be used for testing and debuging.
**/
class SimpleScaleObject extends iron.Trait {

	@prop
	var speed:Float = 0.1;

	var keyboard:Keyboard;
	var rb:RigidBody;

	public function new() {
		super();

		notifyOnInit(function() {
			rb = object.getTrait(RigidBody);
			keyboard = Input.getKeyboard();
		});

		notifyOnUpdate(function() {
			var scale = Vec4.zero();

			if(keyboard.down("y")){
				scale.x += speed;
			}

			if(keyboard.down("u")){
				scale.x -= speed;
			}

			if(keyboard.down("h")){
				scale.y += speed;
			}

			if(keyboard.down("j")){
				scale.y -= speed;
			}

			if(keyboard.down("n")){
				scale.z += speed;
			}

			if(keyboard.down("m")){
				scale.z -= speed;
			}

			if(keyboard.down("up")){
				scale.set(speed, speed, speed);
			}

			if(keyboard.down("down")){
				scale.set(-speed, -speed, -speed);
			}

			if(!scale.equals(Vec4.zero())){
				scaleObject(scale);
			}
		});
	}

	function scaleObject(vec:Vec4){
		var s = object.transform.scale;
		if(rb != null){
			rb.transform.scale = new Vec4(s.x + vec.x, s.y + vec.y, s.z + vec.z);
			rb.syncTransform();
		} else {
			object.transform.scale = new Vec4(s.x + vec.x, s.y + vec.y, s.z + vec.z);
			object.transform.buildMatrix();
		}
	}
}
