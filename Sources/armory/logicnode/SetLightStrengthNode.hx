package armory.logicnode;

import iron.object.LampObject;

class SetLightStrengthNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var light:LampObject = inputs[1].get();
		var strength:Float = inputs[2].get();
		
		if (light == null) return;

		light.data.raw.strength = light.data.raw.type == "sun" ? strength * 0.325 : strength * 0.026;

		super.run();
	}
}
