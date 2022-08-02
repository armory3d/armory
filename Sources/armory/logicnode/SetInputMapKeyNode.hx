package armory.logicnode;

import armory.system.InputMap;

class SetInputMapKeyNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var inputMap = inputs[1].get();
		var key = inputs[2].get();
		var scale = inputs[3].get();
		var deadzone = inputs[4].get();
		var index = inputs[5].get();

		var i = InputMap.getInputMap(inputMap);

		if (i == null) {
			i = InputMap.addInputMap(inputMap);
		}

		var k = InputMap.getInputMapKey(inputMap, key);

		if (k == null) {
			switch(property0) {
				case "keyboard": k = i.addKeyboard(key, scale);
				case "mouse": k = i.addMouse(key, scale, deadzone);
				case "gamepad": {
					k = i.addGamepad(key, scale, deadzone);
					k.setIndex(index);
				}
			}
		
		} else {
			k.scale = scale;
			k.deadzone = deadzone;
			k.setIndex(index);
		}

		runOutput(0);
	}
}
