package armory.logicnode;

class VectorNode extends Node {

	public static inline var _x = 0; // Float
	public static inline var _y = 1; // Float
	public static inline var _z = 2; // Float

	public function new() {
		super();
	}

	public static function create(x:Float, y:Float, z:Float):VectorNode {
		var n = new VectorNode();
		n.inputs.push(FloatNode.create(x));
		n.inputs.push(FloatNode.create(y));
		n.inputs.push(FloatNode.create(z));
		return n;
	}
}
