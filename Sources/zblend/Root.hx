package zblend;

import lue.App;
import lue.Eg;

class Root {

	//var cam:CameraNode;

	public function new() {

		// var modelRes = Eg.getModelResource("budha_resource");
		// var materialRes = Eg.getMaterialResource("material_resource");
		// var lightRes = Eg.getLightResource("light_resource");
		// var camRes = Eg.getCameraResource("camera_resource");

		// var model = Eg.addModelNode(modelRes, materialRes);
		// Eg.setNodeTransform(model, 0, 0, 0, 0, 0, 0);

		// cam = Eg.addCameraNode(camRes);
		// Eg.setNodeTransform(cam, 0, -5, 4.0, -1.3, 0, 0);
		
		// var light = Eg.addLightNode(lightRes);
		// Eg.setNodeTransform(light, -0.5, -4, 2);

		App.requestRender(render);
	}

	function render(g:kha.graphics4.Graphics) {
		//Eg.render(g, cam);
	}
}
