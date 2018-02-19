package armory.logicnode;

import iron.object.Object;
import iron.math.Mat4;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class TranslateOnLocalAxisNode extends LogicNode {

var loc = new Vec4();
var vec = new Vec4();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		var sp:Float = inputs[2].get();
		var l:Int = inputs[3].get();
		var ini:Bool = inputs[4].get();

		if (object == null) return;

		if (l==1){
		loc.setFrom(object.transform.world.look());
		}
		if (l==2){
		loc.setFrom(object.transform.world.up());
		}
		if (l==3){
		loc.setFrom(object.transform.world.right());
		}
			
		if (ini){
			loc.x=-loc.x;
			loc.y=-loc.y;
			loc.z=-loc.z;
		}	
						
		vec.x=loc.x*sp;
		vec.y=loc.y*sp;
		vec.z=loc.z*sp;
		
		object.transform.loc.add(vec);
		object.transform.buildMatrix();
		
		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) rigidBody.syncTransform();
		#end

		super.run();
	}
}