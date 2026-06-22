package armory.logicnode;

import iron.object.LightObject;

class SetLightColorNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var light: LightObject = inputs[1].get();
		var color: iron.math.Vec4 = inputs[2].get();

		if (light == null) return;

		light.data.raw.color[0] = color.x;
		light.data.raw.color[1] = color.y;
		light.data.raw.color[2] = color.z;

		runOutput(0);
	}
}
