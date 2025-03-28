package armory.logicnode;

import iron.object.Object;

class GetObjectGroupNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
	
		var object: Object = inputs[0].get();
		
		var col: Array<String> = [];
		
		if(object == null) return null;
	
		var raw = iron.Scene.active.raw;
		
		for (g in raw.groups){
			if(iron.Scene.active.getGroup(g.name).indexOf(object) != -1) col.push(g.name);
			
		}
			
		return from == 0 ? col : col.length;
	}
}
