package armory.logicnode;

class SetMouseLockNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var lock: Bool = inputs[1].get();
		var mouse = iron.system.Input.getMouse();
		lock ? mouse.lock() : mouse.unlock();
		runOutput(0);
	}
}
