package armory.trait.internal;

#if js

@:expose("iron")
class Bridge {

	public static var App = iron.App;
	public static var Scene = iron.Scene;
	public static var Time = iron.system.Time;
	public static var Input = iron.system.Input;
	public static var Object = iron.object.Object;
	public static var Data = iron.data.Data;
	public static var Vec4 = iron.math.Vec4;
	public static var Quat = iron.math.Quat;
	public static function log(s: String) { trace(s); };
}

#end
