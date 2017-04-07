package armory.logicnode;

class ScriptNode extends Node {

	public var property0:String;
	var result:Dynamic;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {

		var expr = property0;
		var parser = new hscript.Parser();
		var ast = parser.parseString(expr);
		var interp = new hscript.Interp();
		result = interp.execute(ast);

		runOutputs(0);
	}

	override function get(from:Int):Dynamic {
		return result;
	}
}
