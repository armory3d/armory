package armory;

import iron.App;
import iron.Root;
import iron.node.Node;
import iron.node.CameraNode;
import iron.resource.SceneFormat;
import iron.resource.Resource;
import armory.trait.internal.PhysicsWorld;

class Scene {

	var cam:CameraNode;

	public static var physics:PhysicsWorld;

	public function new(sceneId:String) {
		
		// Startup scene
		var sceneNode = Root.addScene(sceneId);

		if (Root.cameras.length == 0) {
			trace('No camera found for scene "$sceneId"!');
			return;
		}
		cam = Root.cameras[0];
		
		// Attach world to camera for now
		var resource:TSceneFormat = Resource.getSceneResource(sceneId);
		cam.world = Resource.getWorld(sceneId, resource.world_ref);

		// Physics
		physics = new PhysicsWorld(resource.gravity);
		sceneNode.addTrait(physics);

		App.notifyOnRender(render);

		// Experimental scene reloading
		// App.notifyOnUpdate(function() {
		// 	if (iron.sys.Input.released) {
		// 		// kha.Assets.loadBlob(sceneId + '_arm', function(b:kha.Blob) {
		// 			iron.App.reset();
		// 			iron.resource.Resource.clearSceneData();
		// 			new iron.App(armory.Root);
		// 		// });
		// 	}
		// });
	}

	function render(g:kha.graphics4.Graphics) {
		cam.renderFrame(g, Root.root, Root.lights);
	}
}
