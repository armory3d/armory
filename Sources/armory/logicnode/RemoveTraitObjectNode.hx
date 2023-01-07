package armory.logicnode;

import iron.object.Object;

class RemoveTraitObjectNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var traitName: String = inputs[2].get();

		assert(Error, object != null, "Object should not be null");
		assert(Error, traitName != null, "Trait name should not be null");

		var cname = Type.resolveClass(Main.projectPackage + "." + traitName);
		if (cname == null) cname = Type.resolveClass(Main.projectPackage + ".node." + traitName);
		assert(Error, cname != null, 'No trait with the name "$traitName" found, make sure that the trait is exported!');
		
		if(object.getTrait(cname) != null)
			object.removeTrait(object.getTrait(cname));

		runOutput(0);
	}
}
