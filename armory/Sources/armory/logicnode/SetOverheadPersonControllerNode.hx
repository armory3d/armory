package armory.logicnode;

import iron.object.Object;


class SetOverheadPersonControllerNode extends LogicNode {

    public function new(tree: LogicTree) {
        super(tree);
    }

    override function run(from: Int): Void {
        // Control de las var de OverheadPersonController...
		// Control OverheadPersonController var
        var objectTrait: Object = inputs[1].get();
        
        // Ajustes de la camara. // Camera settings
        var smoothTrack: Bool = inputs[2].get();
        var smoothSpeed: Float = inputs[3].get();

        // Ajustes de desplazamiento.. // Move setting
        var moveSpeed: Float = inputs[4].get();
        var runSpeed: Float = inputs[5].get();

        // var bool para activar/desactivar las prop del trait (OverheadPersonController)
		// var bool to set true/false the trait props (OverheadPersonController)
        var enableJump: Bool = inputs[6].get();
        var allowAirJump: Bool = inputs[7].get();
        var canRun: Bool = inputs[8].get();
        var stamina: Bool = inputs[9].get();
        var enableFatigue: Bool = inputs[10].get();

        if (objectTrait == null) return;

        // Tomar el trait del object (ovController). // Get trait from (objectTrait) and assigned to the var (ovController)
        var ovController: armory.trait.OverheadPersonController = objectTrait.getTrait(armory.trait.OverheadPersonController);
        if (ovController != null) {

            // Ajustes del suavizado de la camara
			// Setting smoothCamera
            ovController.smoothTrack = smoothTrack;
            ovController.smoothSpeed = smoothSpeed;
            // Ajuste de desplazamiento
			// Setting move
            ovController.moveSpeed = moveSpeed;
            ovController.runSpeed = runSpeed;


            // Ajustes de salto, correr, stamina y fariga()
			// Settings (run, jump, stamina anad fatigue)
            ovController.enableJump = enableJump;
            ovController.allowAirJump = allowAirJump;
            ovController.canRun = canRun;
            ovController.stamina = stamina;
            ovController.enableFatigue = enableFatigue;

        } else {
            // Alertar al usuario si es que no tiene el trait asigando al objeto.
			// Alert the user if they do not have the trait assigning to the object..
            trace("ERROR: The object '" + objectTrait.name + "' does not have the OverheadPersonController script assigning(assign it from (Object->add trait->bundle)).");
        }

        runOutput(0);
    }

}
