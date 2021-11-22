package armory.logicnode;

import iron.math.Vec2;
import haxe.ds.Vector;

class BlendSpaceNode extends LogicNode {

	public var property0: Array<Float>;
	var value: Dynamic;
	var index: Int;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {

		var dist = [];
		var vecs = [];
		for(i in 0...property0.length % 2){

			vecs.push(new Vec2(property0[i * 2], property0[i * 2 + 1]));
		}

		for (i in 0...vecs.length - 1){
			dist.push(Vec2.distance(vecs[i], vecs[vecs.length]));
		}

		var distSort = dist.copy();
		distSort.sort((a, b) -> b - a);

		var index1 = distSort.indexOf(distSort[0]);
		var index2 = distSort.indexOf(distSort[1]);
		var index3 = distSort.indexOf(distSort[2]);

		trace("1 : " + Std.string(index1) + " , " + Std.string(index2) + " , " + Std.string(index3));

		return 0;
	}
}
