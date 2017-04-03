package armory.logicnode;

class OnUpdateNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);

		trait.notifyOnUpdate(update);
	}

	function update() {
		run();
	}
}
