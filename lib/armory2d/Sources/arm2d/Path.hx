package arm2d;

class Path {

	public static function toRelative(path:String, cwd:String):String {
		path = haxe.io.Path.normalize(path);
		cwd = haxe.io.Path.normalize(cwd);

		var ar:Array<String> = [];
		var ar1 = path.split("/");
		var ar2 = cwd.split("/");

		var index = 0;
		while (ar1[index] == ar2[index]) index++;

		for (i in 0...ar2.length - index) ar.push("..");

		for (i in index...ar1.length) ar.push(ar1[i]);

		return ar.join("/");
	}

	public static function toAbsolute(path:String, cwd:String):String {
		return haxe.io.Path.normalize(cwd + "/" + path);
	}
}
