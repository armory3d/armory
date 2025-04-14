package armory.logicnode;
import haxe.Json;

class JsonStringifyNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from: Int):Dynamic {
		return Json.stringify(inputs[0].get());
	}
	
}
