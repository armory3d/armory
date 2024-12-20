package armory.logicnode;

import iron.math.Vec4;
import iron.math.RayCaster;

class DistanceScreenToWorldSpaceNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var vInput: Vec4 = new Vec4();
		vInput.x = inputs[0].get();
		vInput.y = inputs[1].get();

		var cam = iron.Scene.active.camera;
		if (cam == null) return null;

		return (inputs[2].get().y) - cam.transform.world.getLoc().y / RayCaster.getRay(vInput.x, vInput.y, cam).direction.y;
		//return RayCaster.getRay(vInput.x, vInput.y, cam).distanceToPoint(inputs[2].get());
	
	}
}