package armory.logicnode;

class ScriptNode extends LogicNode {

	public var property0:String;
	var result:Dynamic;

	#if arm_hscript
	var parser:hscript.Parser = null;
	var interp:hscript.Interp = null;
	var ast:hscript.Expr = null;
	#end

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {

		var v:Dynamic = inputs[1].get();

		#if arm_hscript
		if (parser == null) {
			parser = new hscript.Parser();
			parser.allowJSON = true;
			parser.allowTypes = true;
			ast = parser.parseString(property0);
			interp = new hscript.Interp();
			interp.variables.set("Math", Math);
		}
		interp.variables.set("input", v);
		result = interp.execute(ast);
		#end

		runOutputs(0);
	}

	override function get(from:Int):Dynamic {
		return result;
	}
}
