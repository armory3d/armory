package armory.trait.navigation;

#if arm_navigation
import haxerecast.Recast;
import armory.trait.NavMesh;
#end

class Navigation extends iron.Trait {

#if (!arm_navigation)
	public function new() { super(); }
#else

	public static var active: Navigation = null;

	public var navMeshes: Array<NavMesh> = [];
	public var recast: Recast;

	public function new() {
		super();
		active = this;

		recast = new Recast();
	}
#end
}
