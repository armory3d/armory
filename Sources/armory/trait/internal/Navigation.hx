package armory.trait.internal;

#if arm_navigation
import haxerecast.Recast;
import armory.trait.NavMesh;
#end

@:keep
class Navigation extends iron.Trait {

#if (!arm_navigation)
	public function new() { super(); }
#else

	public static var active:Navigation = null;
	
	public var navMeshes:Array<NavMesh> = [];
	public var recast:Recast;

	public function new() {
		super();
		active = this;

		recast = untyped __js__("(1, eval)('this').recast");
	}
#end
}
