package armory.trait;

import iron.Trait;
import iron.Root;

class SceneInstance extends Trait {

    public function new(sceneName:String) {
        super();

        notifyOnInit(function() {
			Root.addScene(sceneName, object);
		});
    }
}
