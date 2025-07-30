package armory.logicnode;

import iron.math.Vec4;
import armory.trait.navigation.Navigation;

class NavigableLocationNode extends LogicNode {

	var loc: Vec4;

	public function new(tree: LogicTree) {
		super(tree);

	}

	override function get(from: Int): Dynamic {
#if arm_navigation
	
		assert(Error, Navigation.active.navMeshes.length > 0, "No Navigation Mesh Present");
		Navigation.active.navMeshes[0].getRandomPoint(function(p: Vec4) {
			loc = p;
		});
#end
		return loc;
	}
}
