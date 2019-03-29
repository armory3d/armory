package armory.logicnode;

import iron.object.Object;
import iron.math.Mat4;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class TranslateObjectNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var object:Object = inputs[1].get();
		var vec:Vec4 = inputs[2].get();
		var local:Bool = inputs[3].get();
		var look:Vec4; var right:Vec4; var up:Vec4;

		if (object == null || vec == null) return;

		if(!local) {
		object.transform.loc.add(vec);
		object.transform.buildMatrix();
		}
		else {
			look = object.transform.world.look().mult(vec.x);
			right = object.transform.world.right().mult(vec.y);
			up = object.transform.world.up().mult(vec.z);
			object.transform.loc.add(look);
			object.transform.loc.add(right);
			object.transform.loc.add(up);
			object.transform.buildMatrix();
		}
		
		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) rigidBody.syncTransform();
		#end

		runOutput(0);
	}
	function multVecs(a:Vec4, b:Vec4):Vec4{
		var r; r = new Vec4();
		r.x=a.x*b.x;
		r.y=a.y*b.y;
		r.z=a.z*b.z;
		return r;
	}
}
