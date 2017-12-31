package armory.trait.physics.bullet;

#if arm_bullet

import iron.math.Vec4;
import iron.math.Mat4;
import iron.Trait;
import iron.object.MeshObject;
import iron.data.MeshData;
import iron.data.SceneFormat;
import armory.trait.physics.RigidBody;
import armory.trait.physics.PhysicsWorld;
import haxebullet.Bullet;

class PhysicsHook extends Trait {

	var target:Object;
	var targetName:String;
	var targetTransform:Transform;
	var verts:Array<Float>;
	var hook_rb:BtRigidBody;

	public function new(targetName:String, verts:Array<Float>) {
		super();

		this.targetName = targetName;
		this.verts = verts;

		Scene.active.notifyOnInit(function() {
			notifyOnInit(init);
			notifyOnUpdate(update);
		});
	}

	function init() {
		// Hook to empty axes
		target = targetName != "" ? iron.Scene.active.getChild(targetName) : null;
		targetTransform = target != null ? target.transform : object.transform;

		var physics = PhysicsWorld.active;

		// Soft body hook
	#if arm_physics_soft
		var sb:SoftBody = object.getTrait(SoftBody);
		if (sb != null && sb.ready) {

			// Place static rigid body at target location
			var _inertia = BtVector3.create(0, 0, 0);
			var _shape = BtSphereShape.create(0.01);
			var _transform = BtTransform.create();
			_transform.setIdentity();
			_transform.setOrigin(BtVector3.create(
				targetTransform.loc.x,
				targetTransform.loc.y,
				targetTransform.loc.z));
			_transform.setRotation(BtQuaternion.create(
				targetTransform.rot.x,
				targetTransform.rot.y,
				targetTransform.rot.z,
				targetTransform.rot.w));
			var _centerOfMassOffset = BtTransform.create();
			_centerOfMassOffset.setIdentity();
			var _motionState = BtDefaultMotionState.create(_transform, _centerOfMassOffset);
			var mass = 0.0;
			_shape.calculateLocalInertia(mass, _inertia);
			var _bodyCI = BtRigidBodyConstructionInfo.create(mass, _motionState, _shape, _inertia);
			hook_rb = BtRigidBody.create(_bodyCI);

			#if js
			var nodes = sb.body.get_m_nodes();
			#elseif cpp
			var nodes = sb.body.m_nodes;
			#end

			var geom = cast(object, MeshObject).data.geom;
			var numNodes = Std.int(geom.positions.length / 3);
			for (i in 0...numNodes) {
				var node = nodes.at(i);
				#if js
				var nodePos = node.get_m_x();
				#elseif cpp
				var nodePos = node.m_x;
				#end

				// Find nodes at marked vertex group locations
				var numVerts = Std.int(verts.length / 3);
				for (j in 0...numVerts) {
					var x = verts[j * 3] + sb.vertOffsetX;
					var y = verts[j * 3 + 1] + sb.vertOffsetY;
					var z = verts[j * 3 + 2] + sb.vertOffsetZ;

					// Anchor node to rigid body
					if (Math.abs(nodePos.x() - x) < 0.01 && Math.abs(nodePos.y() - y) < 0.01 && Math.abs(nodePos.z() - z) < 0.01) {
						sb.body.appendAnchor(i, hook_rb, false, 1.0 / numVerts);
					}
				}
			}
			return;
		}
	#end

		// Rigid body hook
		var rb1:RigidBody = object.getTrait(RigidBody);
		if (rb1 != null && rb1.ready) {
			#if js // TODO
			var btrans = BtTransform.create();
			btrans.setIdentity();
			var dx = targetTransform.worldx() - object.transform.worldx();
			var dy = targetTransform.worldy() - object.transform.worldy();
			var dz = targetTransform.worldz() - object.transform.worldz();
			btrans.setOrigin(BtVector3.create(dx, dy, dz));
			var constraint = BtGeneric6DofConstraint.create(rb1.body, btrans, false); // cpp - fix rb1.body pass
			constraint.setLinearLowerLimit(BtVector3.create(0, 0, 0));
			constraint.setLinearUpperLimit(BtVector3.create(0, 0, 0));
			constraint.setAngularLowerLimit(BtVector3.create(-10, -10, -10));
			constraint.setAngularUpperLimit(BtVector3.create(10, 10, 10));
			physics.world.addConstraint(constraint, false);
			#end
			return;
		}

		// Rigid body or soft body not initialized yet
		notifyOnInit(init);
	}

	function update() {
		var _transform = BtTransform.create();
		_transform.setIdentity();
		_transform.setOrigin(BtVector3.create(
			targetTransform.world.getLoc().x,
			targetTransform.world.getLoc().y,
			targetTransform.world.getLoc().z));
		_transform.setRotation(BtQuaternion.create(
			targetTransform.world.getQuat().x,
			targetTransform.world.getQuat().y,
			targetTransform.world.getQuat().z,
			targetTransform.world.getQuat().w));
		hook_rb.setWorldTransform(_transform);
	}

}

#end
