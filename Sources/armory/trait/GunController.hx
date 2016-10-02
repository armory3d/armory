package armory.trait;

import iron.math.Mat4;
import iron.math.Vec4;
import iron.Trait;
import iron.system.Input;
import iron.system.Time;
import iron.object.Object;
import iron.object.Transform;
import iron.object.CameraObject;
import armory.trait.internal.RigidBody;
import armory.system.Keymap;

class GunController extends Trait {

#if (!WITH_PHYSICS)
	public function new() { super(); }
#else

	var projectileRef:String;
	var firePointRef:String;
	var firePoint:Transform;
	var fireStrength = 25;

	public function new(projectileRef:String, firePointRef:String) {
		super();

		this.projectileRef = projectileRef;
		this.firePointRef = firePointRef;
		notifyOnInit(init);
	}
	
	function init() {
		firePoint = object.getChild(firePointRef).transform;
		kha.input.Keyboard.get().notify(onDown, null);
	}

	function onDown(key: kha.Key, char: String) {
		if (char == Keymap.fire) {
			shoot();
		}
	}

	function shoot() {
		// Spawn projectile
		Scene.active.spawnObject(projectileRef, null, function(o:Object) {
			o.transform.loc.x = firePoint.absx();
			o.transform.loc.y = firePoint.absy();
			o.transform.loc.z = firePoint.absz();
			// Apply force
			var rb:RigidBody = o.getTrait(RigidBody);
			rb.notifyOnReady(function() {
				var look = object.transform.look().normalize();
				rb.setLinearVelocity(look.x * fireStrength, look.y * fireStrength, look.z * fireStrength);
			});
			// Remove projectile after a period of time
			kha.Scheduler.addTimeTask(function() {
				o.remove();
			}, 10);
		});
	}

#end
}
