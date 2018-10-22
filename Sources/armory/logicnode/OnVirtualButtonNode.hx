package armory.logicnode;

class OnVirtualButtonNode extends LogicNode {

	public var property0:String;
	public var property1:String;

	public function new(tree:LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {
		var vb = iron.system.Input.getVirtualButton(property1);
		if (vb == null) return;
		var b = false;
		switch (property0) {
		case "Down":
			b = vb.down;
		case "Started":
			b = vb.started;
		case "Released":
			b = vb.released;
		}
		if (b) runOutput(0);
	}
}
