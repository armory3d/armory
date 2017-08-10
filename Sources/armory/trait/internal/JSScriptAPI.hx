package armory.trait.internal;

#if cpp

class JSScriptAPI { }

#else

@:expose("armory")
class JSScriptAPI {

	public static var App = iron.App;
	public static var Scene = iron.Scene;
	public static var Time = iron.system.Time;
	public static var Object = iron.object.Object;
	public static var Data = iron.data.Data;

	public function new() { }
}

@:expose("armory.math")
class JSScriptAPIMath {

	public static var Vec4 = iron.math.Vec4;
	public static var Mat4 = iron.math.Mat4;
	public static var Quat = iron.math.Quat;
}

#end
