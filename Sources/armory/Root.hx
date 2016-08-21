package armory;

import iron.App;
import iron.node.Node;
import iron.node.CameraNode;
import iron.resource.SceneFormat;
import iron.resource.Resource;
import armory.trait.internal.PhysicsWorld;

// #if WITH_EXPOSE
@:expose
// #end
class Root {

	var cam:CameraNode;

	public static var physics:PhysicsWorld;

	public function new() {

		// Startup scene
		var sceneNode = iron.Root.addScene(Main.projectScene);
		cam = iron.Root.cameras[0];
		
		// Attach world to camera for now
		var resource:TSceneFormat = Resource.getSceneResource(Main.projectScene);
		cam.world = Resource.getWorld(Main.projectScene, resource.world_ref);

		// Physics
		physics = new PhysicsWorld(resource.gravity);
		sceneNode.addTrait(physics);

		App.notifyOnRender(render);

		// Experimental scene reloading
		// App.notifyOnUpdate(function() {
		// 	if (iron.sys.Input.released) {
		// 		// kha.Assets.loadBlob(Main.projectScene + '_arm', function(b:kha.Blob) {
		// 			iron.App.reset();
		// 			iron.resource.Resource.clearSceneData();
		// 			new iron.App(armory.Root);
		// 		// });
		// 	}
		// });
	}

	function render(g:kha.graphics4.Graphics) {
		cam.renderFrame(g, iron.Root.root, iron.Root.lights);
	}
}
