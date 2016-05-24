package cycles;

import lue.App;
import lue.Eg;
import lue.node.RootNode;
import lue.node.CameraNode;
import lue.resource.SceneFormat;
import lue.resource.Resource;
import cycles.trait.PhysicsWorld;

class Root {

	var cam:CameraNode;

	public static var physics:PhysicsWorld;

	public function new() {

		// Startup scene
		var sceneNode = Eg.addScene(Main.projectScene);
		cam = RootNode.cameras[0];
		
		// Attach world to camera for now
		var resource:TSceneFormat = Resource.getSceneResource(Main.projectScene);
		cam.world = Resource.getWorld(Main.projectScene, resource.world_ref);

		// Physics
		physics = new PhysicsWorld();
		Eg.addNodeTrait(sceneNode, physics);

		App.requestRender(render);
	}

	function render(g:kha.graphics4.Graphics) {
		Eg.render(g, cam);
	}
}
