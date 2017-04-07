package armory.logicnode;

class ActiveCameraNode extends Node {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic { return armory.Scene.active.camera; }
}
