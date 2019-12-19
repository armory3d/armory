package armory.logicnode;

class WriteJsonNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		// Relative or absolute path to file
		var file: String = inputs[1].get();
		var data: Dynamic = inputs[2].get();
		var s = haxe.Json.stringify(data);
		trace(s);

		#if kha_krom
		var path = Krom.getFilesLocation() + "/" + file;
		var bytes = haxe.io.Bytes.ofString(s);
		Krom.fileSaveBytes(path, bytes.getData());
		#end
	}
}
