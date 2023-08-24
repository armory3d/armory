package armory.logicnode;

class ArrayDisplayNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var ar: Array<Dynamic> = inputs[0].get();
		
		var separator: String = inputs[1].get();
		
		var prop: String = null;
		
		if(property0 != 'Item')
			prop = inputs[2].get();
		
		if(property0 == 'Item')
			return ar.join(separator);
		else if(property0 == 'Item Field')
			return [for (v in ar) Reflect.field(v, prop)].join(separator);
		else if(property0 == 'Item Property')
			return [for (v in ar) Reflect.field(v.properties.h, prop)].join(separator);
			
		return null;
	
	}
}
