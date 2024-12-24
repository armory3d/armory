package armory.logicnode;
import haxe.Json;

class ParseJsonNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from: Int):Dynamic {
		return Json.parse(inputs[0].get());
	}
}
