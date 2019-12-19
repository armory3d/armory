package armory.logicnode;

class ArraySliceNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var ar: Array<Dynamic> = inputs[0].get();
		if (ar == null) return null;

		var i: Int = inputs[1].get();
		var end: Int = inputs[2].get();

		if (i < 0) i = ar.length + i;
		if (i < 0 || i > ar.length - 1) {
			var className = Type.getClassName(Type.getClass(tree));
			var traitName = className.substring(className.lastIndexOf(".") + 1);
			var objectName = tree.object.name;
			trace('Logic error (object: $objectName, trait: $traitName): Array Get - index out of range');
			return null;
		}

		return ar.slice(i, end);
	}
}
