package armory.trait;

import iron.Trait;
import iron.math.Vec4;
import iron.system.Input;
import iron.object.Object;
import iron.object.CameraObject;
import armory.trait.physics.PhysicsWorld;
import armory.trait.physics.RigidBody;
import kha.System;

class OverheadPersonController extends Trait {
    
    #if (!arm_physics)
    public function new() { super(); }
    #else
    
    // Nota: Dejo establecido que el eje (+Y) sera considerada la "cara" del personaje 
	// I established that the axis (+Y) will be considered the "face" of the character. 
    // Camara
    @prop public var cameraFollow:CameraObject;
    @prop public var smoothTrack:Bool = false;
    @prop public var smoothSpeed:Float = 5.0;
    
    @prop public var enableJump:Bool = true;
    @prop public var jumpForce:Float = 22.0;
    @prop public var moveSpeed:Float = 500.0;
    @prop public var forwardKey:String = "w";
    @prop public var backwardKey:String = "s";
    @prop public var leftKey:String = "a";
    @prop public var rightKey:String = "d";
    @prop public var jumpKey:String = "space";
    @prop public var allowAirJump:Bool = false;
    @prop public var canRun:Bool = true;
    @prop public var runKey:String = "shift";
    @prop public var runSpeed:Float = 1000.0;

    // Sistema de estamina
    @prop public var stamina:Bool = false;
    @prop public var staminaBase:Float = 75.0;
    @prop public var staRecoverPerSec:Float = 5.0;
    @prop public var staDecreasePerSec:Float = 5.0;
    @prop public var staRecoverTime:Float = 2.0;
    @prop public var staDecreasePerJump:Float = 5.0;
    @prop public var enableFatigue:Bool = false;
    @prop public var fatigueSpeed:Float = 0.5;  // the reduction of movement when fatigue is activated... // reduccion de movimiento con la fatiga activada 
    @prop public var fatigueThreshold:Float = 30.0; // Tiempo corriendo sin parar para la activacion // Time running non-stop for activation...
    @prop public var fatRecoveryThreshold:Float = 7.5; // Tiempo sin correr/saltar para salir de fatiga // Time without running/jumping to get rid of fatigue...

    // Variables privadas
    var body:RigidBody;

    // var de la camara (camera vars)
    var initialCameraLoc:Vec4;
    var initialOffset:Vec4;
    var currentPos:Vec4;

    var moveForward:Bool = false;
    var moveBackward:Bool = false;
    var moveLeft:Bool = false;
    var moveRight:Bool = false;
    var isRunning:Bool = false;
    var canJump:Bool = true;
    var staminaValue:Float = 0.0;
    var timeSinceStop:Float = 0.0;
    var fatigueTimer:Float = 0.0;
    var fatigueCooldown:Float = 0.0;
    var isFatigueActive:Bool = false;

    var dir:Vec4 = new Vec4();

    public function new() {
        super();
        iron.Scene.active.notifyOnInit(init);
    }

    // Ajustes para la camara y la rotaicon del "jugador" 
	// Settings for the camera and the "player" rotation
    function init() {
        body = object.getTrait(RigidBody);

        if (cameraFollow == null) {
			// Alertar al usuario en caso de no asignar una camara. // Alert the user if a camera is not assigned
            trace("[OverheadCameraController] a camera was not assigned to 'cameraFollow'."); 
        } else {
            // Guardar la posicion inicial de la camara // Save the initial position of the camera
            initialCameraLoc = cameraFollow.transform.loc.clone();
            // Calcular el offset relativo al jugador // Calculate the offset relative to the player
            initialOffset = initialCameraLoc.sub(object.transform.loc);
            currentPos = initialCameraLoc.clone();
        }

        PhysicsWorld.active.notifyOnPreUpdate(preUpdate);
        notifyOnUpdate(update);
        notifyOnRemove(removed);
        staminaValue = staminaBase;
    }

    function removed() {
        PhysicsWorld.active.removePreUpdate(preUpdate);
    }

    function preUpdate() {
        if (Input.occupied || body == null) return;
        var mouse = Input.getMouse();

        var screenW = System.windowWidth();
        var screenH = System.windowHeight();

        // Posicion relativa del mouse respecto al centro de la pantalla 
		// Relative position of the mouse with respect to the center of the screen
        var mouseXRel = mouse.x - screenW / 2;
        var mouseYRel = mouse.y - screenH / 2;
		
        // Angulo 360° usando atan2 (invertido para corregir direccion) // 360° angle using atan2 (inverted to correct direction) 
        var angleZ = -Math.atan2(mouseXRel, -mouseYRel);
        object.transform.setRotation(object.transform.rot.x, object.transform.rot.y, angleZ);

        body.syncTransform();

        // Camara siguiendo al jugador (manteniendo offset inicial) // Camera following the player (maintaining initial offset)
        if (cameraFollow != null) {
            var playerPos = object.transform.loc;
            var targetPos = new Vec4(
                playerPos.x + initialOffset.x,
                playerPos.y + initialOffset.y,
                playerPos.z + initialOffset.z,
                1 // w 1 (posicion absoluta)
				// used w=1 to indicate that the camera position is an absolute point in the world...
            );
			// Mover la camara a 'targetPos' de forma gradual o instantanea si 'smoothTrack' es false
			// Moves the camera to 'targetPos' gradually or instantly if 'smoothTrack' is false
            if (smoothTrack) {
                var delta = targetPos.sub(currentPos);
                var moveStep = delta.mult(smoothSpeed * iron.system.Time.delta);
                if (moveStep.length() > delta.length()) moveStep = delta;
                currentPos = currentPos.add(moveStep);
                cameraFollow.transform.loc.setFrom(currentPos);
            } else {
                currentPos = targetPos.clone();
                cameraFollow.transform.loc.setFrom(currentPos);
            }
        }
    }

    function isFatigued():Bool {
        return enableFatigue && isFatigueActive;
    }

    function update() {
        if (body == null) return;
        var deltaTime:Float = iron.system.Time.delta;
        var kb = Input.getKeyboard();

        moveForward = kb.down(forwardKey);
        moveBackward = kb.down(backwardKey);
        moveLeft = kb.down(leftKey);
        moveRight = kb.down(rightKey);
        var isMoving = moveForward || moveBackward || moveLeft || moveRight;

        var isGrounded:Bool = false;
        #if arm_physics
        var vel = body.getLinearVelocity();
        if (Math.abs(vel.z) < 0.1) isGrounded = true;
        #end

        // Dejo establecido el salto para tener en cuenta (isFatigued)
		// I set the jump to take into account the (isFatigued) 
        if (isGrounded && !isFatigued()) {
            canJump = true;
        }
        // Saltar con estamina // Jump with stamina
        if (enableJump && kb.started(jumpKey) && canJump) {
            var jumpPower = jumpForce;
            // Disminuir el salto al 50% si la (stamina) esta por debajo o en el 20%. // Decrease jump to 50% if stamina is below or at 20%
            if (stamina) {
                if (staminaValue <= 0) {
                    jumpPower = 0;
                } else if (staminaValue <= staminaBase * 0.2) {
                    jumpPower *= 0.5;
                }

                staminaValue -= staDecreasePerJump;
                if (staminaValue < 0.0) staminaValue = 0.0;
                timeSinceStop = 0.0;
            }

            if (jumpPower > 0) {
                body.applyImpulse(new Vec4(0, 0, jumpPower));
                if (!allowAirJump) canJump = false;
            }
        }

        // Control de estamina y correr // Control of stamina and running 
        if (canRun && kb.down(runKey) && isMoving) {
            if (stamina) {
                if (staminaValue > 0.0) {
                    isRunning = true;
                    staminaValue -= staDecreasePerSec * deltaTime;
                    if (staminaValue < 0.0) staminaValue = 0.0;
                } else {
                    isRunning = false;
                }
            } else {
                isRunning = true;
            }
        } else {
            isRunning = false;
        }

        // (temporizadores aparte) (fatigue system timers)
        if (isRunning) {
            timeSinceStop = 0.0;
            fatigueTimer += deltaTime;
            fatigueCooldown = 0.0;
        } else {
            timeSinceStop += deltaTime;
            fatigueCooldown += deltaTime;
        }

        // Evitar correr y saltar al estar fatigado // Avoid running and jumping when fatigued
        if (isFatigued()) {
             isRunning = false;
             canJump = false;
        }

        // Activar fatiga despues de correr continuamente durante cierto umbral 
		// Activate fatigue after running continuously for a certain threshold
        if (enableFatigue && fatigueTimer >= fatigueThreshold) {
            isFatigueActive = true;
        }

        // Eliminar la fatiga despues de recuperarse // Eliminate fatigue after recovery (fatRecoveryThreshold)
        if (enableFatigue && isFatigueActive && fatigueCooldown >= fatRecoveryThreshold) {
            isFatigueActive = false;
            fatigueTimer = 0.0;
        }

        // Recuperar estamina si no esta corriendo // Recover stamina if you re not running ()
        if (stamina && !isRunning && staminaValue < staminaBase && !isFatigued()) {
            if (timeSinceStop >= staRecoverTime) {
                staminaValue += staRecoverPerSec * deltaTime;
                if (staminaValue > staminaBase) staminaValue = staminaBase;
            }
        }

        // Movimiento en ejes globales // Movement on global axies
        dir.set(0,0,0);
        if (moveForward)  dir.add(new Vec4(0, 1, 0, 0));
        if (moveBackward) dir.add(new Vec4(0,-1, 0, 0));
        if (moveRight)    dir.add(new Vec4(1, 0, 0, 0));
        if (moveLeft)     dir.add(new Vec4(-1,0, 0, 0));

        var btvec = body.getLinearVelocity();
        body.setLinearVelocity(0.0, 0.0, btvec.z - 1.0);
		// Movement speed control (final) (run and fatigued when are true/false) 
        if (dir.length() > 0) {
            var dirN = dir.normalize();
            var baseSpeed = moveSpeed;
            if (isRunning) baseSpeed = runSpeed;
            var currentSpeed = isFatigued() ? baseSpeed * fatigueSpeed : baseSpeed;
            dirN.mult(currentSpeed * deltaTime);
            body.activate();
            body.setLinearVelocity(dirN.x, dirN.y, btvec.z - 1.0);
        }

        body.setAngularFactor(0,0,0);
        if (cameraFollow != null) cameraFollow.buildMatrix();
    }

    #end
}


// Stamina and fatigue system.....

