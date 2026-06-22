package armory.logicnode;

class MergedVirtualButtonNode extends LogicNode {

	public var property0: String;
	public var property1: String;

	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	function update() {
		var vb = iron.system.Input.getVirtualButton(property1);
		if (vb == null) return;
		var b = false;
		switch (property0) {
		case "started":
			b = vb.started;
		case "down":
			b = vb.down;
		case "released":
			b = vb.released;
		}
		if (b) runOutput(0);
	}

	override function get(from: Int): Dynamic {
		var vb = iron.system.Input.getVirtualButton(property1);
		if (vb == null) return false;
		switch (property0) {
		case "started":
			return vb.started;
		case "down":
			return vb.down;
		case "released":
			return vb.released;
		}
		return false;
	}
}
