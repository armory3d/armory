package armory.logicnode;

class TraitNode extends LogicNode {

	public var property0:String;
	public var value:Dynamic = null;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic { 
		// if (value == null) value = new Trait(); // TODO
		return value;
	}

	override function set(value:Dynamic) {
		this.value = value;
	}
}
