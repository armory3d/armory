package armory.trait;

import iron.Trait;
import iron.math.Vec4;
import iron.system.Input;
import iron.object.Object;
import iron.object.CameraObject;
import armory.trait.physics.PhysicsWorld;
import armory.trait.physics.RigidBody;
import kha.FastFloat;

class FirstPersonController extends Trait {

    #if (!arm_physics)
    public function new() { super(); }
    #else

    @prop public var rotationSpeed:Float = 0.15;
    @prop public var maxPitch:Float = 2.2;
    @prop public var minPitch:Float = 0.5;
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
    @prop public var runVelocity:Float = 1000.0;

    // Sistema de estamina
    @prop public var stamina:Bool = false;
    @prop public var staminaBase:Float = 75.0;
    @prop public var staRecoverPerSec:Float = 5.0;
    @prop public var staDecreasePerSec:Float = 5.0;
    @prop public var staRecoverTime:Float = 2.0;
    @prop public var staDecreasePerJump:Float = 5.0;
    @prop public var enableFatigue:Bool = false;
    @prop public var fatigueSpeed:Float = 0.5;  // the reduction of movement when fatigue is activated... 
    @prop public var fatigueThreshold:Float = 30.0; // Tiempo corriendo sin parar para la activacion // Time running non-stop for activation...
    @prop public var fatRecoveryThreshold:Float = 7.5; // Tiempo sin correr/saltar para salir de fatiga // Time without running/jumping to get rid of fatigue...
    

    // Var Privadas 
    var head:CameraObject;
    var pitch:Float = 0.0;
    var body:RigidBody;

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

    public function new() {
        super();
        iron.Scene.active.notifyOnInit(init);
    }

    function init() {
        body = object.getTrait(RigidBody);
        head = object.getChildOfType(CameraObject);
        PhysicsWorld.active.notifyOnPreUpdate(preUpdate);
        notifyOnUpdate(update);
        notifyOnRemove(removed);
        staminaValue = staminaBase;
    }

    function removed() {
        PhysicsWorld.active.removePreUpdate(preUpdate);
    }

    var zVec = Vec4.zAxis();

    function preUpdate() {
        if (Input.occupied || body == null) return;
        var mouse = Input.getMouse();
        var kb = Input.getKeyboard();

        if (mouse.started() && !mouse.locked)
            mouse.lock();
        else if (kb.started("escape") && mouse.locked)
            mouse.unlock();

        if (mouse.locked || mouse.down()) {
            var deltaTime:Float = iron.system.Time.delta;
            object.transform.rotate(zVec, -mouse.movementX * rotationSpeed * deltaTime);
            var deltaPitch:Float = -(mouse.movementY * rotationSpeed * deltaTime);
            pitch += deltaPitch;
            pitch = Math.max(minPitch, Math.min(maxPitch, pitch));
            head.transform.setRotation(pitch, 0.0, 0.0);
            body.syncTransform();
        }
    }

    var dir:Vec4 = new Vec4();

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
        if (Math.abs(vel.z) < 0.1) {
            isGrounded = true;
        }
        #end

        // Dejo establecido el salto para tener en cuenta la (enableFatigue) si es que es false/true....
		if (isGrounded && !isFatigued()) {
		    canJump = true;
		}
        // Saltar con estamina
        if (enableJump && kb.started(jumpKey) && canJump) {
            var jumpPower = jumpForce;
            // Disminuir el salto al 50% si la (stamina) esta por debajo o en el 20%.
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

        // Control de estamina y correr
        if (canRun && kb.down(runKey) && isMoving) {
            if (stamina) {
                if (staminaValue > 0.0) {
                    isRunning = true;
                    staminaValue -= staDecreasePerSec * deltaTime;
                    if (staminaValue < 0.0) staminaValue = 0.0;
                    timeSinceStop = 0.0;
                    fatigueTimer += deltaTime;
                    fatigueCooldown = 0.0;
                } else {
                    isRunning = false;
                }
            } else {
                isRunning = true;
                timeSinceStop = 0.0;
                fatigueTimer += deltaTime;
                fatigueCooldown = 0.0;
            }
        } else {
            isRunning = false;
            timeSinceStop += deltaTime;
            fatigueCooldown += deltaTime;
        }

        // Evitar correr y saltar al estar fatigado...
        if (isFatigued()) {
   			 isRunning = false;
   			 canJump = false;
		}

        // Activar fatiga después de correr continuamente durante cierto umbral
        if (enableFatigue && fatigueTimer >= fatigueThreshold) {
            isFatigueActive = true;
        }

        // Eliminar la fatiga despues de recuperarse
        if (enableFatigue && isFatigueActive && fatigueCooldown >= fatRecoveryThreshold) {
            isFatigueActive = false;
            fatigueTimer = 0.0;
        }

        // Recuperar estamina si no está corriendo
        if (stamina && !isRunning && staminaValue < staminaBase && !isFatigued()) {
            if (timeSinceStop >= staRecoverTime) {
                staminaValue += staRecoverPerSec * deltaTime;
                if (staminaValue > staminaBase) staminaValue = staminaBase;
            }
        }

        // Movimiento
        dir.set(0, 0, 0);
        if (moveForward) dir.add(object.transform.look());
        if (moveBackward) dir.add(object.transform.look().mult(-1));
        if (moveLeft) dir.add(object.transform.right().mult(-1));
        if (moveRight) dir.add(object.transform.right());

        var btvec = body.getLinearVelocity();
        body.setLinearVelocity(0.0, 0.0, btvec.z - 1.0);

        if (isMoving) {
            var dirN = dir.normalize();
            var baseSpeed = moveSpeed;
            if (isRunning && moveForward) {
                baseSpeed = runVelocity;
            }
            var currentSpeed = isFatigued() ? baseSpeed * fatigueSpeed : baseSpeed;
            var currentSpeed = isFatigued() ? baseSpeed * fatigueSpeed : baseSpeed;
            dirN.mult(currentSpeed * deltaTime);
            body.activate();
            body.setLinearVelocity(dirN.x, dirN.y, btvec.z - 1.0);
        }

        body.setAngularFactor(0, 0, 0);
        head.buildMatrix();
    }

    #end
}


// Stamina and fatigue system.....
