package armory.logicnode;

class MergedMouseNode extends LogicNode {

	public var property0:String;
	public var property1:String;

	public function new(tree:LogicTree) {
		super(tree);
		
		tree.notifyOnUpdate(update);
	}
	
	function update() {
		var mouse = iron.system.Input.getMouse();
		var b = false;
		switch (property0) {
		case "Down":
			b = mouse.down(property1);
		case "Started":
			b = mouse.started(property1);
		case "Released":
			b = mouse.released(property1);
		case "Moved":
			b = mouse.moved;
		}
		if (b) runOutput(0);
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
