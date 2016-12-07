package armory.logicnode;

#if arm_navigation
import armory.trait.internal.Navigation;
#end

import armory.trait.internal.NodeExecutor;
import iron.math.Vec4;

class NavigableLocationNode extends LocationNode {

	public function new() {
		super();
	}

	public override function start(executor:NodeExecutor, parent:Node = null) {
		super.start(executor, parent);

		executor.notifyOnNodeInit(init);
	}

	function init() {
		getPoint();
	}

	override public function consumed() {
		getPoint();
	}

	function getPoint() {
#if arm_navigation
		// Assume navmesh exists..
		Navigation.active.navMeshes[0].getRandomPoint(function(p:iron.math.Vec4) {
			loc = p;
		});
#end
	}

	public static function create(target:iron.object.Object):NavigableLocationNode {
		var n = new NavigableLocationNode();
		return n;
	}
}
