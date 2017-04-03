package armory.logicnode;

class TimeNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function get(from:Int):Dynamic {
		return armory.system.Time.time();
	}
}
