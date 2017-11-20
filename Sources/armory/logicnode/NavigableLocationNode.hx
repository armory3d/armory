package armory.logicnode;

import iron.math.Vec4;
import armory.trait.navigation.Navigation;

class NavigableLocationNode extends LogicNode {

	var loc:Vec4;

	public function new(tree:LogicTree) {
		super(tree);

		iron.Scene.active.notifyOnInit(function() {
			get(0);
		});
	}

	override function get(from:Int):Dynamic {
#if arm_navigation
		// Assume navmesh exists..
		Navigation.active.navMeshes[0].getRandomPoint(function(p:Vec4) {
			loc = p;
		});
#end
		return loc;
	}
}
