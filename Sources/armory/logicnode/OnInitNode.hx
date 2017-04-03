package armory.logicnode;

class OnInitNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);

		trait.notifyOnInit(init);
	}

	function init() {
		run();
	}
}
