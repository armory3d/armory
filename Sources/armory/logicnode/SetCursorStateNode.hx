package armory.logicnode;

class SetCursorStateNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var state: Bool = inputs[1].get();
		var mouse = iron.system.Input.getMouse();

		switch (property0) {
		case "hide locked":
			state ? mouse.hide() : mouse.show();
 			mouse.hidden ? mouse.lock() : mouse.unlock();

 		case "hide":
 			state ? mouse.hide() : mouse.show();
 
 		case "lock":
 			state ? mouse.lock() : mouse.unlock();
		}

		runOutput(0);
	}
}
