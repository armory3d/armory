package armory.logicnode;

class ArrayShuffleNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var ar: Array<Dynamic> = inputs[0].get();
		
		var t = [], array = [];
		
		for(i in 0...ar.length)
			t.push(i);
		
		while (t.length > 0) {
			var pos = Std.random(t.length), index = t[pos];
			t.splice(pos, 1);
			array.push(ar[index]);
		}
		
		return array;
	}
}


