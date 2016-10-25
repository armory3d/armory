package armory.trait.internal;

import iron.Trait;
import iron.object.Object;
import iron.object.Transform;
import iron.system.Input;
import iron.math.RayCaster;

@:keep
class EditorSpace extends Trait {

	var gizmo:Object;
	var arrowX:Object;
	var arrowY:Object;
	var arrowZ:Object;
	var selected:Transform = null;

	var moveX = false;
	var moveY = false;
	var moveZ = false;

	static var first = true;

	public function new() {
		super();
		
		notifyOnInit(init);
	}

	function init() {
		// gizmo = iron.Scene.active.getChild('ArrowGizmo');
		// arrowX = iron.Scene.active.getChild('ArrowX');
		// arrowY = iron.Scene.active.getChild('ArrowY');
		// arrowZ = iron.Scene.active.getChild('ArrowZ');

		notifyOnUpdate(update);

		if (first) {
			first = false;
			kha.input.Keyboard.get().notify(onKeyDown, onKeyUp);
		}
	}

	function onKeyDown(key: kha.Key, char: String) {
		if (char == 'Z' || key == kha.Key.ESC) trace('__arm|quit');
	}

	function onKeyUp(key: kha.Key, char: String) {
	}

	function update() {

		if (Input.started2) {
			var transforms:Array<Transform> = [];
			for (o in iron.Scene.active.meshes) transforms.push(o.transform);
			var hit = RayCaster.getClosestBoxIntersect(transforms, Input.x, Input.y, iron.Scene.active.camera);
			if (hit != null) {
				var loc = hit.loc;
				// gizmo.transform.loc.set(loc.x, loc.y, loc.z);
				// gizmo.transform.buildMatrix();
				selected = hit;
				trace('__arm|select|' + selected.object.name);
			}
		}

		// if (selected != null) {
		// 	if (Input.started) {

		// 		var transforms = [arrowX.transform, arrowY.transform, arrowZ.transform];

		// 		var hit = RayCaster.getClosestBoxIntersect(transforms, Input.x, Input.y, iron.Scene.active.camera);
		// 		if (hit != null) {
		// 			if (hit.object.name == 'ArrowX') moveX = true;
		// 			else if (hit.object.name == 'ArrowY') moveY = true;
		// 			else if (hit.object.name == 'ArrowX') moveZ = true;
		// 		}
		// 	}

		// 	if (moveX || moveY || moveZ) {
		// 		Input.occupied = true;

				
		// 		if (moveX) selected.loc.x += Input.deltaX / 110.0;
		// 		if (moveY) selected.loc.y += Input.deltaX / 110.0;
		// 		if (moveZ) selected.loc.z += Input.deltaX / 110.0;
				
		// 		selected.buildMatrix();

		// 		// gizmo.transform.loc.set(selected.loc.x, selected.loc.y, selected.loc.z);
		// 		// gizmo.transform.buildMatrix();
		// 	}
		// }

		// if (Input.released) {
		// 	Input.occupied = false;
		// 	// Move operator creator into separate class..
		// 	// Map directly to bl operators - setx to translate
		// 	if (moveX) trace('__arm|setx|' + selected.object.name + '|' + selected.loc.x);
		// 	moveX = moveY = moveZ = false;
		// }
	}
}
