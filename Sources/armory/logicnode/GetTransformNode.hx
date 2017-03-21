package armory.logicnode;

class GetTransformNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function get():Dynamic {
		var object = inputs[1].get();
		return object.transform.matrix;
	}
}
