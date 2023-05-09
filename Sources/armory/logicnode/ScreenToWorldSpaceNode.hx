package armory.logicnode;

import iron.math.Vec4;
import iron.math.RayCaster;

class ScreenToWorldSpaceNode extends LogicNode {

	public var property0: Bool; // Separator Out

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var vInput: Vec4 = new Vec4();
		vInput.x = inputs[0].get();
		vInput.y = inputs[1].get();

		var cam = iron.Scene.active.camera;
		if (cam == null) return null;

		// Separator Out
		if (property0) {
			switch (from) {
				// World
				case 0: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).origin;
				}
				// World X
				case 1: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).origin.x;
				}
				// World Y
				case 2: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).origin.y;
				}
				// World Z
				case 3: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).origin.z;
				}
				// Direction
				case 4: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).direction.normalize();
				}
				// Direction X
				case 5: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).direction.normalize().x;
				}
				// Direction Y
				case 6: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).direction.normalize().y;
				}
				// Direction Z
				case 7: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).direction.normalize().z;
				}
			}
		}
		else
		{
			switch (from) {
				// World
				case 0: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).origin;
				}
				// Direction
				case 1: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).direction.normalize();
				}
			}	
		}
		return null;
	}
}
