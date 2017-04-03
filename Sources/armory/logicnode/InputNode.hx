package armory.logicnode;

class InputNode extends Node {

	public var property0:String;

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function get(from:Int):Dynamic {
		switch (property0) {
		case "Down":
			return armory.system.Input.down;
		case "Started":
			return armory.system.Input.started;
		case "Released":
			return armory.system.Input.released;
		case "Moved":
			return armory.system.Input.moved;
		}
		return false;
	}
}
