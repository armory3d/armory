package armory.trait.internal;

import iron.Trait;
import iron.object.Object;
import iron.object.Transform;
import iron.sys.Input;
import iron.math.RayCaster;

class SceneEditor extends Trait {

    var gizmo:Object;
    var arrowX:Object;
    var arrowY:Object;
    var arrowZ:Object;
    var selected:Transform = null;

    var moveX = false;
    var moveY = false;
    var moveZ = false;

    public function new() {
        super();
        
        notifyOnInit(init);
    }

    function init() {
        gizmo = iron.Scene.active.getObject('ArrowGizmo');
        arrowX = iron.Scene.active.getObject('ArrowX');
        arrowY = iron.Scene.active.getObject('ArrowY');
        arrowZ = iron.Scene.active.getObject('ArrowZ');

        notifyOnUpdate(update);
    }

    function update() {

        if (Input.started2) {
            var transforms:Array<Transform> = [];
            for (o in iron.Scene.active.meshes) transforms.push(o.transform);
            var hit = RayCaster.getClosestBoxIntersect(transforms, Input.x, Input.y, iron.Scene.active.camera);
            if (hit != null) {
                var loc = hit.loc;
                gizmo.transform.loc.set(loc.x, loc.y, loc.z);
                gizmo.transform.buildMatrix();
                selected = hit;
            }
        }

        if (selected != null) {
            if (Input.started) {

                var transforms = [arrowX.transform, arrowY.transform, arrowZ.transform];

                var hit = RayCaster.getClosestBoxIntersect(transforms, Input.x, Input.y, iron.Scene.active.camera);
                if (hit != null) {
                    if (hit.object.name == 'ArrowX') moveX = true;
                    else if (hit.object.name == 'ArrowY') moveY = true;
                    else if (hit.object.name == 'ArrowX') moveZ = true;
                }
            }

            if (moveX || moveY || moveZ) {
                Input.occupied = true;

                
                if (moveX) selected.loc.x += Input.deltaX / 100.0;
                if (moveY) selected.loc.y += Input.deltaX / 100.0;
                if (moveZ) selected.loc.z += Input.deltaX / 100.0;
                
                selected.buildMatrix();

                gizmo.transform.loc.set(selected.loc.x, selected.loc.y, selected.loc.z);
                gizmo.transform.buildMatrix();
            }
        }

        if (Input.released) {
            Input.occupied = false;
            // Move operator creator into separate class..
            // Map directly to bl operators - setx to translate
            if (moveX) trace('__arm|setx|' + selected.object.name + '|' + selected.loc.x);
            moveX = moveY = moveZ = false;
        }
    }
}
