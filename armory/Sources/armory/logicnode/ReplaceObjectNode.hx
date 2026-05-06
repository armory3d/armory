package armory.logicnode;

import iron.object.Object;
import iron.math.Quat;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class ReplaceObjectNode extends LogicNode {

    public function new(tree: LogicTree) {
        super(tree);
    }

    override function run(from: Int) {
        var base: Object = inputs[1].get();
        var replace: Object = inputs[2].get();
        var invert: Bool = inputs[3].get();
        var includeScale: Bool = inputs[4].get();

        if (base == null || replace == null) return;

        // Obtener posicion, rotacion y escala global de ambos obj // get position, rotation and global scale of both obj
        var baseLoc = base.transform.world.getLoc().clone();
        var replaceLoc = replace.transform.world.getLoc().clone();

        var tmpVec = new Vec4();
        var baseRot = new Quat();
        var replaceRot = new Quat();
        var tmpScale = new Vec4();

        base.transform.world.decompose(tmpVec, baseRot, tmpScale);
        replace.transform.world.decompose(tmpVec, replaceRot, tmpScale);

        var baseScale = base.transform.scale.clone();
        var replaceScale = replace.transform.scale.clone();

        if (!invert) {
            // Intercambiar transformaciones // Swap transformations
            base.transform.loc.setFrom(replaceLoc);
            base.transform.rot.setFrom(replaceRot);
            if (includeScale) base.transform.scale.setFrom(replaceScale);

            replace.transform.loc.setFrom(baseLoc);
            replace.transform.rot.setFrom(baseRot);
            if (includeScale) replace.transform.scale.setFrom(baseScale);
        } else {
            // Invertir: cada (object) vuelve a su lugar inicial // Invert: each (object) returns to its initial place
            base.transform.loc.setFrom(baseLoc);
            base.transform.rot.setFrom(baseRot);
            if (includeScale) base.transform.scale.setFrom(baseScale);

            replace.transform.loc.setFrom(replaceLoc);
            replace.transform.rot.setFrom(replaceRot);
            if (includeScale) replace.transform.scale.setFrom(replaceScale);
        }

        // Recalcular matrices
        base.transform.buildMatrix();
        replace.transform.buildMatrix();

        // Sincronizar RB // Sync RB
        #if arm_physics
        for (obj in [base, replace]) {
            var rb = obj.getTrait(RigidBody);
            if (rb != null) rb.syncTransform();
        }
        #end

        runOutput(0);
    }
}
