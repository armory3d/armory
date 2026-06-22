package armory.logicnode;

import iron.object.Object;

class GetTraitNode extends LogicNode {

	var cname: Class<iron.Trait> = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();
		var name: String = inputs[1].get();

		if (object == null) return null;
		if (cname == null) cname = cast Type.resolveClass(Main.projectPackage + "." + name);
		if (cname == null) cname = cast Type.resolveClass(Main.projectPackage + ".node." + name);

		return object.getTrait(cname);
	}
}
