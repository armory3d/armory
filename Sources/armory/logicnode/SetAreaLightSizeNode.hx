package armory.logicnode;

import iron.object.LightObject;

class SetAreaLightSizeNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var light: LightObject = inputs[1].get();
		var size: Float = inputs[2].get();
		var size_y: Float = inputs[3].get();

		if (light == null) return;
		
		light.data.raw.size = size;
		light.data.raw.size_y = size_y;

		runOutput(0);
	}
}
