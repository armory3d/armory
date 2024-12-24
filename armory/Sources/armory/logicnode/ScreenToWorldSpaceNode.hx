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
				// At
				case 0: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).at(inputs[2].get());
				}
				// Origin
				case 1: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).origin;
				}
				// Origin X
				case 2: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).origin.x;
				}
				// Origin Y
				case 3: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).origin.y;
				}
				// Origin Z
				case 4: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).origin.z;
				}
				// Direction
				case 5: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).direction;
				}
				// Direction X
				case 6: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).direction.x;
				}
				// Direction Y
				case 7: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).direction.y;
				}
				// Direction Z
				case 8: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).direction.z;
				}
			}
		}
		else
		{
			switch (from) {
				// At
				case 0: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).at(inputs[2].get());
				}
				// Origin
				case 1: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).origin;
				}
				// Direction
				case 2: {
					return RayCaster.getRay(vInput.x, vInput.y, cam).direction;
				}
			}	
		}
		return null;
	}
}
