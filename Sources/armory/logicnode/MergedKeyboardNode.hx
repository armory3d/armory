package armory.logicnode;

class MergedKeyboardNode extends LogicNode {

	public var property0:String;
	public var property1:String;

	public function new(tree:LogicTree) {
		super(tree);
		
		tree.notifyOnUpdate(update);
	}
	
	function update() {
		var keyboard = iron.system.Input.getKeyboard();
		var b = false;
		switch (property0) {
		case "Down":
			b = keyboard.down(property1);
		case "Started":
			b = keyboard.started(property1);
		case "Released":
			b = keyboard.released(property1);
		}
		if (b) runOutput(0);
	}
	
	override function get(from:Int):Dynamic {
		var keyboard = iron.system.Input.getKeyboard();
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
