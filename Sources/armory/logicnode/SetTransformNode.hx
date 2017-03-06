package armory.logicnode;

class SetTransformNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function run() {
		var object = inputs[1].get();
		var transform = inputs[2].get();

		object.transform.setMatrix(transform);

		super.run();
	}
}
