package armory.logicnode;

class ExpressionNode extends LogicNode {

	public var property0: String;
	var result: Dynamic;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {

		#if hscript
		var expr = property0;
		var parser = new hscript.Parser();
		var ast = parser.parseString(expr);
		var interp = new hscript.Interp();
		result = interp.execute(ast);
		#end

		runOutput(0);
	}

	override function get(from: Int): Dynamic {
		return result;
	}
}
