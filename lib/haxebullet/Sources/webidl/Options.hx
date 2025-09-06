package webidl;

typedef Options = {
	var idlFile : String;
	var nativeLib : String;
	@:optional var outputDir : String;
	@:optional var includeCode : String;
	@:optional var chopPrefix : String;
	@:optional var autoGC : Bool;
}