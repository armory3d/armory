package armory.logicnode;

class SetMouseLockNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(node:LogicNode) {
		var lock:Bool = inputs[1].get();
		var mouse = iron.system.Input.getMouse();
		lock ? mouse.lock() : mouse.unlock();
		super.run(this);
	}
}
