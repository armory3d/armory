package armory.logicnode;

class TraitNode extends LogicNode {

	public var property0: String;
	public var value: Dynamic = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		if (value != null) return value;

		var cname = Type.resolveClass(Main.projectPackage + "." + property0);
		if (cname == null) cname = Type.resolveClass(Main.projectPackage + ".node." + property0);
		if (cname == null) throw 'No trait with the name "$property0" found, make sure that the trait is exported!';
		value = Type.createInstance(cname, []);
		return value;
	}

	override function set(value: Dynamic) {
		this.value = value;
	}
}
