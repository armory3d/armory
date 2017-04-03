package armory.logicnode;

class SelfNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function get(from:Int):Dynamic { return trait.object; }
}
