package armory.logicnode;

import iron.object.LightObject;

class SetLightShadowNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var light: LightObject = inputs[1].get();
		var shadow: Bool = inputs[2].get();

		if (light == null) return;

		light.data.raw.cast_shadow = shadow;

		runOutput(0);
	}
}
