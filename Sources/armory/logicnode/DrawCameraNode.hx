package armory.logicnode;

import iron.RenderPath;
import iron.Scene;
import iron.math.Vec2;
import iron.object.CameraObject;

import armory.renderpath.RenderPathCreator;

class DrawCameraNode extends LogicNode {
	static inline var numStaticInputs = 2;

	var cameras: Array<CameraObject>;
	var renderTargets: Array<kha.Image>;
	var positions: Array<Vec2>;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		switch (from) {
			case 0: // Start
				if (cameras == null) {
					final numDynamicInputs = inputs.length - numStaticInputs;
					final numCams = Std.int(numDynamicInputs / 5);

					// Preallocate
					cameras = [];
					cameras.resize(numCams);

					positions = [];
					positions.resize(numCams);
					for (i in 0...positions.length) {
						positions[i] = new Vec2();
					}

					renderTargets = [];
					renderTargets.resize(numCams);
				}

				for (i in 0...cameras.length) {
					cameras[i] = inputs[numStaticInputs + i * 5].get();
					positions[i].set(
						inputs[numStaticInputs + i * 5 + 1].get(),
						inputs[numStaticInputs + i * 5 + 2].get()
					);

					// TODO: implement proper rendertarget cache/pool
					renderTargets[i] = kha.Image.createRenderTarget(
						inputs[numStaticInputs + i * 5 + 3].get(), // w
						inputs[numStaticInputs + i * 5 + 4].get(), // h
						kha.graphics4.TextureFormat.RGBA32,
						kha.graphics4.DepthStencilFormat.NoDepthAndStencil
					);
				}

				tree.notifyOnRender(render);
				tree.notifyOnRender2D(render2D);
				runOutput(0);

			case 1: // Stop
				tree.removeRender(render);
				tree.removeRender2D(render2D);
				runOutput(1);
		}
	}

	function render(g:kha.graphics4.Graphics) {
		final rpPaused = RenderPath.active.paused;
		RenderPath.active.paused = false;

		final sceneCam = iron.Scene.active.camera;

		for (i in 0...cameras.length) {
			final cam = cameras[i];

			final oldRT = cam.renderTarget;
			cam.renderTarget = renderTargets[i];

			iron.Scene.active.camera = cam;
			cam.renderFrame(g);

			cam.renderTarget = oldRT;
		}

		iron.Scene.active.camera = sceneCam;
		RenderPath.active.paused = rpPaused;
	}

	function render2D(g: kha.graphics2.Graphics) {
		for(i in 0...cameras.length) {
			final rt = renderTargets[i];

			final posX = positions[i].x;
			final posY = positions[i].y;

			g.color = 0xff000000;
			g.fillRect(posX, posY, rt.width, rt.height);
			g.color = 0xffffffff;
			g.drawScaledImage(rt, posX, posY, rt.width, rt.height);
		}
	}
}
