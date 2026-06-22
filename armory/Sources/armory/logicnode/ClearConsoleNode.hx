package armory.logicnode;

class ClearConsoleNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {

		#if kha_krom
			Krom.sysCommand("cls");
		#elseif kha_html5
			js.Syntax.code("console.clear();");
		#end

		runOutput(0);
	}
}
