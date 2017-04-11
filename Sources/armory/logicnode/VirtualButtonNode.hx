package armory.logicnode;

class VirtualButtonNode extends LogicNode {

	public var property0:String;
	public var property1:String;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var vb = armory.system.Input.getVirtualButton(property1);
		if (vb == null) return false;
		switch (property0) {
		case "Down":
			return vb.down;
		case "Started":
			return vb.started;
		case "Released":
			return vb.released;
		}
		return false;
	}
}
