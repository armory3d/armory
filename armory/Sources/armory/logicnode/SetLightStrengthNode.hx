package armory.logicnode;

import iron.object.LightObject;

class SetLightStrengthNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var light: LightObject = inputs[1].get();
		var strength: Float = inputs[2].get();

		if (light == null) return;

		light.data.raw.strength = light.data.raw.type == "sun" ? strength * 0.325 : strength * 0.026;

		runOutput(0);
	}
}
