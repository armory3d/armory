package armory.logicnode;

class KeyboardNode extends LogicNode {

	public var property0:String;
	public var property1:String;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var keyboard = armory.system.Input.getKeyboard();
		switch (property0) {
		case "Down":
			return keyboard.down(property1);
		case "Started":
			return keyboard.started(property1);
		case "Released":
			return keyboard.released(property1);
		}
		return false;
	}
}
