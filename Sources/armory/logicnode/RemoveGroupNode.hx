package armory.logicnode;

class RemoveGroupNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var groupName:String = inputs[1].get();
		
		iron.Scene.active.groups.remove(groupName);

		runOutput(0);
	}
}
