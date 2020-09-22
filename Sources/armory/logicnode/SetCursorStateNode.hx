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
		case "Hide Locked":
			state ? mouse.hide() : mouse.show();
 			mouse.hidden ? mouse.lock() : mouse.unlock();

 		case "Hide":
 			state ? mouse.hide() : mouse.show();
 
 		case "Lock":
 			state ? mouse.lock() : mouse.unlock();
		}

		runOutput(0);
	}
}
