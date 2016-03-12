package cycles;

import lue.App;
import lue.Eg;
import lue.node.RootNode;
import lue.node.CameraNode;
import cycles.trait.PhysicsWorld;

class Root {

	var cam:CameraNode;

	public static var physics:PhysicsWorld;

	public function new() {

		var sceneNode = Eg.addScene(Main.projectScene);
		cam = RootNode.cameras[0];

		physics = new PhysicsWorld();
		Eg.addNodeTrait(sceneNode, physics);

		App.requestRender(render);
	}

	function render(g:kha.graphics4.Graphics) {
		Eg.render(g, cam);
	}
}
