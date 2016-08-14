package armory;

import iron.App;
import iron.Eg;
import iron.node.Node;
import iron.node.RootNode;
import iron.node.CameraNode;
import iron.resource.SceneFormat;
import iron.resource.Resource;
import armory.trait.internal.PhysicsWorld;

class Root {

	var cam:CameraNode;

	public static var physics:PhysicsWorld;

	public function new() {

		// Startup scene
		var scene = Eg.addScene(Main.projectScene);
		cam = RootNode.cameras[0];
		
		// Attach world to camera for now
		var resource:TSceneFormat = Resource.getSceneResource(Main.projectScene);
		cam.world = Resource.getWorld(Main.projectScene, resource.world_ref);

		// Physics
		physics = new PhysicsWorld(resource.gravity);
		Eg.addNodeTrait(scene, physics);

		App.notifyOnRender(render);
	}

	function render(g:kha.graphics4.Graphics) {
		Eg.render(g, cam);
	}
}
