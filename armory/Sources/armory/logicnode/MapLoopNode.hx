package armory.logicnode;
import iron.math.Vec4;


class MapLoopNode extends LogicNode {
	public var key: Dynamic;
	public var value: Dynamic;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {

		var map: Map<Dynamic,Dynamic> = inputs[1].get();
		if (map == null) return;
		//var keys:Array<Dynamic> = Reflect.fields(map);
		for (k in map.keys()) {
			key = k;
			value = map[k];
			runOutput(0);

			if (tree.loopBreak) {
				tree.loopBreak = false;
				break;
			}
			
			if (tree.loopContinue) {
				tree.loopContinue = false;
				continue;
			}
		}
		runOutput(3);
	}

	override function get(from: Int): Dynamic {
		if (from == 1)
			return key;
		return value;
	}
}
