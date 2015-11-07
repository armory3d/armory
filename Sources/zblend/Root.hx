package zblend;

import lue.App;
import lue.Eg;
import lue.node.CameraNode;

class Root {

	var cam:CameraNode;

	public function new() {

		var sceneNode = Eg.addScene("Scene");
		cam = lue.node.Node.cameras[0];	

		App.requestRender(render);
	}

	function render(g:kha.graphics4.Graphics) {
		Eg.render(g, cam);
	}
}
