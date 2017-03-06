package armory.logicnode;

class TimeNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function get():Dynamic {
		return armory.system.Time.time();
	}
}
