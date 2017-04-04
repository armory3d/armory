package armory.logicnode;

class GetObjectNode extends Node {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var objectName:String = inputs[0].get();

		return armory.Scene.active.getChild(objectName);
	}
}
