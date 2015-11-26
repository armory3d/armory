package cycles.node;

import cycles.trait.NodeExecutor;

class Node {

	var executor:NodeExecutor;

	var parents:Array<Node> = [];
	public var inputs:Array<Dynamic> = [];

	public function new() {}

	public function start(executor:NodeExecutor, parent:Node = null) {
		this.executor = executor;
		if (parent != null) parents.push(parent);

		for (inp in inputs) inp.start(executor, this);

		inputChanged();
	}

	public function inputChanged() {
		for (p in parents) {
			p.inputChanged();
		}
	}
}
