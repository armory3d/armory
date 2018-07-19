package armory.logicnode;

class DisplayInfoNode extends LogicNode {

	static inline var displayIndex = 0;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
#if (kha_version < 1807) // TODO: deprecated
		if (from == 0) return kha.Display.width(displayIndex);
		else return kha.Display.height(displayIndex);
#else
		if (from == 0) return kha.Display.all[displayIndex].width;
		else return kha.Display.all[displayIndex].height;
#end
	}
}
