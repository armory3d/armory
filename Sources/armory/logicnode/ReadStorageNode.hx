package armory.logicnode;

class ReadStorageNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var key: String = inputs[0].get();

		var data: Dynamic = iron.system.Storage.data;
		if (data == null) return null;

		var value: Dynamic = Reflect.field(data, key);

		if (value == null) {
			value = parseArg(inputs[1].get());
		}

		return value;
	}

	static function parseArg(str: String): Dynamic {
		if (str == "true") return true;
		else if (str == "false") return false;
		else if (str.charAt(0) == "'") return StringTools.replace(str, "'", "");
		else if (str.charAt(0) == "[") { // Array
			// Remove [] and recursively parse into array,
			// then append into parent
			str = StringTools.replace(str, "[", "");
			str = StringTools.replace(str, "]", "");
			str = StringTools.replace(str, " ", "");
			var ar: Dynamic = [];
			var s = str.split(",");
			for (childStr in s) {
				ar.push(parseArg(childStr));
			}
			return ar;
		}
		else {
			var f = Std.parseFloat(str);
			var i = Std.parseInt(str);
			return f == i ? i : f;
		}
	}
}
