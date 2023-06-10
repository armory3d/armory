package armory.trait;

import iron.Scene;
import iron.object.Object;

/**
   This trait is to be used with a camera mounted on a camera boom with offset.
   1. Place the camera as a child to another object, for example an 'Empty'.
   2. Place this trait on the 'Empty' object.
   3. Set the name of the target object to be followed by the camera.
**/
class FollowCamera extends iron.Trait {

	@prop
	var target: String;

	@prop
	var lerp: Bool = true;

	@prop
	var lerpSpeed: Float = 0.1;

	var targetObj: Object;
	var disabled = false;

	public function new() {
		super();

		notifyOnInit(function() {
			targetObj = Scene.active.getChild(target);
			if (targetObj == null) {
				disabled = true;
				trace("FollowCamera error, unable to set target object");
			}

			if (Std.isOfType(object, iron.object.CameraObject)) {
			 	disabled = true;
				trace("FollowCamera error, this trait should not be placed directly on a camera objet. It should be placed on another object such as an Empty. The camera should be placed as a child to the Empty object with offset, creating a camera boom.");
			}
		});

		notifyOnLateUpdate(function() {
			if (!disabled) {
				if (targetObj != null) {
					if (lerp) {
						object.transform.loc.lerp(object.transform.world.getLoc(), targetObj.transform.world.getLoc(), lerpSpeed);
					}
					else {
						object.transform.loc = targetObj.transform.world.getLoc();
					}
					object.transform.buildMatrix();
				}
				else {
					targetObj = Scene.active.getChild(target);
				}
			}
		});
	}
}
