package armory.logicnode;

class GetObjectNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var objectName:String = inputs[0].get();

		return iron.Scene.active.getChild(objectName);
	}
}
