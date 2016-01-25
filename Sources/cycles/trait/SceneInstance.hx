package cycles.trait;

import lue.trait.Trait;
import lue.Eg;

class SceneInstance extends Trait {

    public function new(sceneId:String) {
        super();

        requestInit(function() {
			Eg.addScene(sceneId, node);
		});
    }
}
