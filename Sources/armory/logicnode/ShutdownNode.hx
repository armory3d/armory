package armory.logicnode;

class ShutdownNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
#if (kha_version < 1807) // TODO: deprecated
		kha.System.requestShutdown();
#else
		kha.System.stop();
#end
	}
}
