package armory.trait.internal;

import iron.Eg;
import iron.math.Mat4;
import iron.math.Vec4;
import iron.Trait;
import iron.node.Transform;
import iron.node.RootNode;
import iron.node.ModelNode;
import iron.resource.MaterialResource.MaterialContext;

class PathTracer extends Trait {

	var context:MaterialContext;
	var ray00Location:Int;
	var ray01Location:Int;
	var ray10Location:Int;
	var ray11Location:Int;
	
	var objectLocations:Array<Int>;
	var transformMap:Map<Int, Transform>;

    public function new() {
        super();

		notifyOnInit(init);
        notifyOnUpdate(update);
    }
	
	function getColorFromNode(node:ModelNode):Array<Float> {
		// Hard code for now
		for (c in node.materials[0].contexts[0].resource.bind_constants) {
			if (c.id == "albedo_color") {
				return c.vec4;
			}
		}
		return null;
	}
	
	function init() {
		context = Eg.getMaterialResource('pt_material').getContext('pt_trace_pass');
		
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
		var cubeNum = 0;
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
						float: n.transform.size.x / 2 - 0.02
					}
				);
				
				var col = getColorFromNode(n);
				context.resource.bind_constants.push(
					{
						id: "sphereColor" + sphereNum,
						vec3: [col[0], col[1], col[2]]
					}
				);
				
				sphereNum++;
			}
			else if (n.id.split(".")[0] == "Cube") {
				context.resource.bind_constants.push(
					{
						id: "cubeCenter" + cubeNum,
						vec3: [0.0, 0.0, 0.0]
					}
				);
				var loc = context.resource.bind_constants.length - 1;
				objectLocations.push(loc);
				transformMap.set(loc, n.transform);
				
				context.resource.bind_constants.push(
					{
						id: "cubeSize" + cubeNum,
						vec3: [n.transform.size.x / 2, n.transform.size.y / 2, n.transform.size.z / 2]
					}
				);
				
				var col = getColorFromNode(n);
				context.resource.bind_constants.push(
					{
						id: "cubeColor" + cubeNum,
						vec3: [col[0], col[1], col[2]]
					}
				);
				
				cubeNum++;
			}
		}
	}

    function update() {
		var camera = RootNode.cameras[0];
		var eye = camera.transform.pos;
		
		// var jitter = Mat4.identity();
		// jitter.initTranslate(Math.random() * 2 - 1, Math.random() * 2 - 1, 0);
		// jitter.multiplyScalar(1 / iron.App.w);
		// jitter.multiplyScalar(1 / 400);
		var mvp = Mat4.identity();
		mvp.mult2(camera.V);
		mvp.mult2(camera.P);
		var inverse = Mat4.identity();
		// jitter.mult2(mvp);
		inverse.inverse2(mvp);
		var matrix = inverse;
		
		// Set uniforms	
		
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
			t.buildMatrix();
			var c = context.resource.bind_constants[loc];
			c.vec3[0] = t.absx();
			c.vec3[1] = t.absy();
			c.vec3[2] = t.absz();
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
