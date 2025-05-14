package armory.logicnode;

import iron.Scene;
import iron.object.CameraObject;

import armory.renderpath.RenderPathCreator;

class DrawCameraTextureNode extends LogicNode {

	var cam: CameraObject;
	var rt: kha.Image;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		switch (from) {
			case 0: // Start
				final o = inputs[3].get();
				assert(Error, Std.isOfType(o, iron.object.MeshObject), "Object must be a mesh object!");
				final mo = cast(o, iron.object.MeshObject);
				final matSlot = inputs[4].get();
				assert(Error, matSlot < o.materials.length, 'Object "${mo.name}" does not have a material slot with index $matSlot!');
				assert(Error, matSlot >= 0, 'Material slot must not be negative. Current value: $matSlot.');

				final c = inputs[2].get();
				assert(Error, Std.isOfType(c, CameraObject), "Camera must be a camera object!");
				cam = cast(c, CameraObject);
				rt = kha.Image.createRenderTarget(iron.App.w(), iron.App.h());

				assert(Error, mo.materials[matSlot].contexts[0].textures != null, 'Object "${mo.name}" has no diffuse texture to render to');
				mo.materials[matSlot].contexts[0].textures[0] = rt; // Override diffuse texture

				tree.notifyOnRender(render);
				runOutput(0);

			case 1: // Stop
				tree.removeRender(render);
				runOutput(1);
		}
	}

	function render(g: kha.graphics4.Graphics) {
		final sceneCam = iron.Scene.active.camera;
		final oldRT = cam.renderTarget;

		iron.Scene.active.camera = cam;
		cam.renderTarget = rt;

		cam.renderFrame(g);

		cam.renderTarget = oldRT;
		iron.Scene.active.camera = sceneCam;
	}
}
