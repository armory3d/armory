package armory.logicnode;

class InitNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);

		trait.notifyOnInit(init);
	}

	function init() {
		run();
	}
}
