package armory.trait.internal;

import iron.Trait;
import iron.Eg;

class SceneInstance extends Trait {

    public function new(sceneId:String) {
        super();

        notifyOnInit(function() {
			Eg.addScene(sceneId, node);
		});
    }
}
