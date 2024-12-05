package armory.logicnode;

import iron.object.LightObject;

class SetSpotLightSizeNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var light: LightObject = inputs[1].get();
		var size: Float = inputs[2].get();

		if (light == null) return;
		
		light.data.raw.spot_size = size;

		runOutput(0);
	}
}