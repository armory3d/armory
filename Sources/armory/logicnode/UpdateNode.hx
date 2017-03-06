package armory.logicnode;

class UpdateNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);

		trait.notifyOnUpdate(update);
	}

	function update() {
		run();
	}
}
