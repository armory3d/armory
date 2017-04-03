package armory.logicnode;

class GetTransformNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function get(from:Int):Dynamic {
		var object = inputs[1].get();

		if (object == null) object = trait.object;

		return object.transform.matrix;
	}
}
