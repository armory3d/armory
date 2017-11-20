package armory.logicnode;

class MouseNode extends LogicNode {

	public var property0:String;
	public var property1:String;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var mouse = iron.system.Input.getMouse();
		switch (property0) {
		case "Down":
			return mouse.down(property1);
		case "Started":
			return mouse.started(property1);
		case "Released":
			return mouse.released(property1);
		case "Moved":
			return mouse.moved;
		}
		return false;
	}
}
