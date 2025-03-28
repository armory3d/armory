package armory.logicnode;

class OnKeyboardNode extends LogicNode {

	public var property0: String;
	public var property1: String;

	@:deprecated("The 'On Keyboard' node is deprecated and will be removed in future SDK versions. Please use 'Keyboard' instead.")
	public function new(tree: LogicTree) {
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
}
