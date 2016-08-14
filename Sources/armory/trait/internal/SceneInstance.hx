package armory.trait.internal;

import iron.Trait;
import iron.Root;

class SceneInstance extends Trait {

    public function new(sceneId:String) {
        super();

        notifyOnInit(function() {
			Root.addScene(sceneId, node);
		});
    }
}
