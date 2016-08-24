package armory;

import iron.App;
import iron.Root;
import iron.object.Object;
import iron.object.CameraObject;
import iron.data.SceneFormat;
import iron.data.Data;
import armory.trait.internal.PhysicsWorld;

class Scene {

	var cam:CameraObject;

	public static var physics:PhysicsWorld;

	public function new(sceneName:String) {
		
		// Startup scene
		var sceneObject = Root.addScene(sceneName);

		if (Root.cameras.length == 0) {
			trace('No camera found for scene "$sceneName"!');
			return;
		}
		cam = Root.cameras[0];
		
		// Attach world to camera for now
		var raw:TSceneFormat = Data.getSceneRaw(sceneName);
		cam.world = Data.getWorld(sceneName, raw.world_ref);

		// Physics
		physics = new PhysicsWorld(raw.gravity);
		sceneObject.addTrait(physics);

		App.notifyOnRender(render);

		// Experimental scene reloading
		// App.notifyOnUpdate(function() {
		// 	if (iron.sys.Input.released) {
		// 		// kha.Assets.loadBlob(sceneName + '_arm', function(b:kha.Blob) {
		// 			iron.App.reset();
		// 			iron.data.Data.clearSceneData();
		// 			new iron.App(armory.Root);
		// 		// });
		// 	}
		// });
	}

	function render(g:kha.graphics4.Graphics) {
		cam.renderFrame(g, Root.root, Root.lamps);
	}
}
