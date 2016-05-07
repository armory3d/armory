package cycles.trait;

import lue.Eg;
import lue.math.Mat4;
import lue.math.Vec4;
import lue.Trait;
import lue.node.Transform;
import lue.node.RootNode;
import lue.resource.MaterialResource.MaterialContext;

class PathTracer extends Trait {

	var context:MaterialContext;
	var eyeLocation:Int;
	var lightLocation:Int;
	var ray00Location:Int;
	var ray01Location:Int;
	var ray10Location:Int;
	var ray11Location:Int;
	
	var objectLocations:Array<Int>;
	var transformMap:Map<Int, Transform>;

    public function new() {
        super();

		requestInit(init);
        requestUpdate(update);
    }
	
	function init() {
		context = Eg.getMaterialResource('pt_material').getContext('pt_trace_pass');
		
		context.resource.bind_constants.push(
			{
				id: "eye",
				vec3: [0.0, 0.0, 0.0]
			}
		);
		eyeLocation = context.resource.bind_constants.length - 1;
		
		context.resource.bind_constants.push(
			{
				id: "light",
				vec3: [0.9, 0.6, 1.1]
			}
		);
		lightLocation = context.resource.bind_constants.length - 1;
		
		context.resource.bind_constants.push(
			{
				id: "glossiness",
				float: 0.6
			}
		);
		
		context.resource.bind_constants.push(
			{
				id: "ray00",
				vec3: [0.0, 0.0, 0.0]
			}
		);
		ray00Location = context.resource.bind_constants.length - 1;
		
		context.resource.bind_constants.push(
			{
				id: "ray01",
				vec3: [0.0, 0.0, 0.0]
			}
		);
		ray01Location = context.resource.bind_constants.length - 1;
		
		context.resource.bind_constants.push(
			{
				id: "ray10",
				vec3: [0.0, 0.0, 0.0]
			}
		);
		ray10Location = context.resource.bind_constants.length - 1;
		
		context.resource.bind_constants.push(
			{
				id: "ray11",
				vec3: [0.0, 0.0, 0.0]
			}
		);
		ray11Location = context.resource.bind_constants.length - 1;
		
		objectLocations = [];
		transformMap = new Map();
		var sphereNum = 0;
		for (n in RootNode.models) {
			if (n.id.split(".")[0] == "Sphere") {
				
				context.resource.bind_constants.push(
					{
						id: "sphereCenter" + sphereNum,
						vec3: [0.0, 0.0, 0.0]
					}
				);
				
				var loc = context.resource.bind_constants.length - 1;
				objectLocations.push(loc);
				transformMap.set(loc, n.transform);
				
				context.resource.bind_constants.push(
					{
						id: "sphereRadius" + sphereNum,
						float: 0.288
					}
				);
				
				sphereNum++;
			}
		}
	}

    function update() {
		var camera = RootNode.cameras[0];
		var eye = camera.transform.pos;
		
		//var jitter = Mat4.identity();
		//jitter.initTranslate(Math.random() * 2 - 1, Math.random() * 2 - 1, 0);
		//jitter.multiplyScalar(1 / lue.App.w);
		var mvp = Mat4.identity();
		mvp.mult2(camera.V);
		mvp.mult2(camera.P);
		var inverse = Mat4.identity();
		// jitter.mult2(mvp);
		inverse.inverse2(mvp);
		var matrix = inverse;
		
		// Set uniforms	
		context.resource.bind_constants[eyeLocation].vec3 = [eye.x, eye.y, eye.z];
		
		var v = getEyeRay(matrix, -1, -1, eye);
		context.resource.bind_constants[ray00Location].vec3 = [v.x, v.y, v.z];
		
		var v = getEyeRay(matrix, -1,  1, eye);
		context.resource.bind_constants[ray01Location].vec3 = [v.x, v.y, v.z];
		
		var v = getEyeRay(matrix,  1, -1, eye);
		context.resource.bind_constants[ray10Location].vec3 = [v.x, v.y, v.z];
		
		var v = getEyeRay(matrix,  1,  1, eye);
		context.resource.bind_constants[ray11Location].vec3 = [v.x, v.y, v.z];
		
		for (loc in objectLocations) {
			var t:Transform = transformMap.get(loc);
			context.resource.bind_constants[loc].vec3[0] = t.absx();
			context.resource.bind_constants[loc].vec3[1] = t.absy();
			context.resource.bind_constants[loc].vec3[2] = t.absz();
		}
    }
	
	function getEyeRay(matrix:Mat4, x:Float, y:Float, eye:Vec4):Vec4 {
		var v = new Vec4();
		var vv = new kha.math.FastVector4(x, y, 0, 1);
		vv = matrix.multvec(vv);
		v.x = vv.x;
		v.y = vv.y;
		v.z = vv.z;
		v.w = vv.w;
		v.x /= v.w;
		v.y /= v.w;
		v.z /= v.w;
		v.w /= v.w;
		v.sub(eye);
		return v;
	}
}
