package armory.logicnode;

import iron.object.Object;


class SetFirstPersonControllerNode extends LogicNode {

    public function new(tree: LogicTree) {
        super(tree);
    }

    override function run(from: Int): Void {
        // Control de las var de FirstPersonController...
		// Control FirstPersonController var
        var object: Object = inputs[1].get();

        // Ajustes de la camara. // Camera settings
        var rotationSpeed: Float = inputs[2].get();
        var maxPitch: Float = inputs[3].get();
        var minPitch: Float = inputs[4].get();
        // Ajustes de desplazamiento.. // Move settings
        var moveSpeed: Float = inputs[5].get();
        var runSpeed: Float = inputs[6].get();


        // var bool para activar/desactivar las prop del trait (FirstPersonController)
		// var bool to set true/false the trait props (FirstPersonController)
        var enableJump: Bool = inputs[7].get();
        var allowAirJump: Bool = inputs[8].get();
        var canRun: Bool = inputs[9].get();
        var stamina: Bool = inputs[10].get();
        var enableFatigue: Bool = inputs[11].get();

        if (object == null) return;

        // Tomar el Trait desde el object (FPController) // Get trait from (object) and assigned to the var (fpController)
        var fpController: armory.trait.FirstPersonController = object.getTrait(armory.trait.FirstPersonController);
        if (fpController != null) {

            // Ajustes de la camara // Cam settings
            fpController.rotationSpeed = rotationSpeed;
            fpController.maxPitch = maxPitch;
            fpController.minPitch = minPitch;
            // Ajuste de desplazamiento // Move settings
            fpController.moveSpeed = moveSpeed;
            fpController.runSpeed = runSpeed;


            // Ajustes de salto, correr, stamina y fariga()
			// Settings (run, jump, stamina anad fatigue)
            fpController.enableJump = enableJump;
            fpController.allowAirJump = allowAirJump;
            fpController.canRun = canRun;
            fpController.stamina = stamina;
            fpController.enableFatigue = enableFatigue;

        } else {
            // Alertar al usuario si es que no tiene el trait asigando al objeto.
			// Alert the user if they do not have the trait assigning to the object.
            trace("ERROR: The object '" + object.name + "' does not have the FirstPersonController script assigning(assign it from (Object->add trait->bundle)).");
        }

        runOutput(0);
    }

}

