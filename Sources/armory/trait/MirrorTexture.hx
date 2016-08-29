package armory.trait;

import iron.Trait;
import iron.object.MeshObject;

class MirrorTexture extends Trait {

    var cameraName:String;

    public function new(cameraName:String) {
        super();

        this.cameraName = cameraName;
        notifyOnInit(init);
    }

    function init() {
		var image = iron.Scene.active.getCamera(cameraName).data.mirror;
		
		var o = cast(object, iron.object.MeshObject);
		o.materials[0].contexts[0].textures[0] = image; // Override diffuse texture
    }
}
