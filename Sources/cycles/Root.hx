package cycles;

import lue.App;
import lue.Eg;
import lue.Env;
import lue.node.RootNode;
import lue.node.CameraNode;
import cycles.trait.PhysicsWorld;

class Root {

	var cam:CameraNode;

	public static var physics:PhysicsWorld;

	public function new() {
		
		// Environment
		if (Main.texEnvironment != "") {
			Env.irradiance = Reflect.field(kha.Assets.images, Main.texEnvironment + "_irradiance");
			Env.radiance = Reflect.field(kha.Assets.images, Main.texEnvironment + "_radiance");
			var radianceMipmaps:Array<kha.Image> = [];
			for (i in 0...Main.texEnvironmentMipmaps) {
				radianceMipmaps.push(Reflect.field(kha.Assets.images, Main.texEnvironment + '_radiance_' + i));
			}
			Env.radiance.setMipmaps(radianceMipmaps);
			Env.brdf = Reflect.field(kha.Assets.images, "envmap_brdf");
		}

		// Startup scene
		var sceneNode = Eg.addScene(Main.projectScene);
		cam = RootNode.cameras[0];

		// Physics
		physics = new PhysicsWorld();
		Eg.addNodeTrait(sceneNode, physics);

		App.requestRender(render);
	}

	function render(g:kha.graphics4.Graphics) {
		Eg.render(g, cam);
	}
}
