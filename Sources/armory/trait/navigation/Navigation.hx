package armory.trait.navigation;

#if arm_navigation
import iron.math.Vec4;

import armory.trait.NavMesh;

class Navigation extends iron.Trait {

	public static var active: Navigation = null;

	public var navMeshes: Array<NavMesh> = [];
	//public var recast: Recast;

	public var debugDrawHelper: DebugDrawHelper = null;

	public function new() {
		super();
		active = this;
		initDebugDrawing();

	}

	function initDebugDrawing() {
		debugDrawHelper = new DebugDrawHelper(this);
	}
}

enum abstract DebugDrawMode(Int) from Int to Int {
	/** All debug flags off. **/
	var NoDebug = 0;

	/** Draw wireframes of the NavMesh. **/
	var DrawWireframe = 1;
}

class RecastConversions {
	public static function recastVec3FromVec4(vec: Vec4): recast.Recast.Vec3{
		return new recast.Recast.Vec3(vec.x, vec.z, vec.y);
	}

	public static function vec4FromRecastVec3(vec: recast.Recast.Vec3): Vec4 {
		return new Vec4(vec.x, vec.z, vec.y);
	}

}
#end