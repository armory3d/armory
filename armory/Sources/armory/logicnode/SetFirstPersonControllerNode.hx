package armory.logicnode;

import iron.object.Object;


class SetFirstPersonControllerNode extends LogicNode {

    public function new(tree: LogicTree) {
        super(tree);
    }

    override function run(from: Int): Void {
        // Script para controlar las var de FirstPersonController...

        var object: Object = inputs[1].get();

        // Ajustes de la camara.
        var rotationSpeed: Float = inputs[2].get();
        var maxPitch: Float = inputs[3].get();
        var minPitch: Float = inputs[4].get();
        // Ajustes de desplazamiento..
        var moveSpeed: Float = inputs[5].get();
        var runSpeed: Float = inputs[6].get();


        // var bool para activar/desactivar las prop del trait (FirstPersonController)
        var enableJump: Bool = inputs[7].get();
        var allowAirJump: Bool = inputs[8].get();
        var canRun: Bool = inputs[9].get();
        var stamina: Bool = inputs[10].get();
        var enableFatigue: Bool = inputs[11].get();

        if (object == null) return;

        // Tomar el Trait desde el objcet(FPController)
        var fpController: armory.trait.FirstPersonController = object.getTrait(armory.trait.FirstPersonController);
        if (fpController != null) {

            // Ajustes con respecto a la rot de la camara
            fpController.rotationSpeed = rotationSpeed;
            fpController.maxPitch = maxPitch;
            fpController.minPitch = minPitch;
            // Ajuste de desplazamiento
            fpController.moveSpeed = moveSpeed;
            fpController.runSpeed = runSpeed;


            // Ajustes de salto, correr, stamina y fariga()
            fpController.enableJump = enableJump;
            fpController.allowAirJump = allowAirJump;
            fpController.canRun = canRun;
            fpController.stamina = stamina;
            fpController.enableFatigue = enableFatigue;

        } else {
            // Alertar al usuario si es que no tiene el trait asigando al objeto.
            trace("ERROR: The object '" + object.name + "' does not have the FirstPersonController script assigning(assign it from (Object->add trait->bundle)).");
        }

        runOutput(0);
    }

}
