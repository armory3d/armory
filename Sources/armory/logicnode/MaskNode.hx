package armory.logicnode;

class MaskNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		
		var ret : Int= 0;	
		for(v in 0...20){
			var bit:Bool = inputs[v].get();
			if(bit) ret |= (1 << v);
		}
		return ret;
	}
}
