package armory.logicnode;

import haxe.io.Bytes;
import haxe.io.BytesInput;
import haxe.io.BytesOutput;
import armory.logicnode.MathExpressionNode.Formula;
import armory.logicnode.MathExpressionNode.FormulaException;

class MathTermNode extends LogicNode {

	public var property0:Bool; // bind param values

	public function new(tree: LogicTree) {
		super(tree);
	}
	
	var simplifyError:String = null;
	var derivateError:String = null;
	var resultError:String = null;
	
	override function get(from: Int): Dynamic {
	
		var error:String = null;
		var errorPos:Int = -1;
		
		var formula:Formula = null;
		
		try {
			formula = new Formula(inputs[0].get());
		}		
		catch(e:FormulaException) {
			error = e.msg;
			errorPos = e.pos;
		}
		
		// bind input values to formula parameters
		if ((error == null) && (property0 || from == 3)) {
			try {
				bindValuesToFormulaParams(formula);
			}		
			catch(e:FormulaException) {
				error = e.msg;
				errorPos = e.pos;
			}
		}
		
		if (from == 0) { // -------- Formula ----------
			return (error == null) ? formula : null;
		}
		else if (from == 1) { // -------- Simplifyed ----------
			var f:Formula = null;
			simplifyError = null;
			if (error == null) {
				try { 
					f = formula.simplify();
				} 
				catch(e:FormulaException) {
					simplifyError = e.msg;
				}
			}
			return f;
		}
		else if (from == 2) { // -------- Derivate ----------
			var f:Formula = null;
			derivateError = null;
			if (error == null) {
				try { 
					f = formula.derivate( inputs[1].get() );
				} 
				catch(e:FormulaException) {
					derivateError = e.msg;
				}
			}
			return f;
		}
		else if (from == 3) { // -------- Result ----------
			var result:Float = 0.0;
			resultError = null;
			if (error == null) {
				try { 
					result = formula.result;
				} 
				catch(e:FormulaException) {
					resultError = e.msg;
				}
			}
			return result;
		}
		else if (from == 4) { // -------- Error ----------
			if (error != null) return error;
			else {
				var errorMessage:String = "";
				if (simplifyError != null) errorMessage += "Simplifyed:" + simplifyError + " ";
				if (derivateError != null) errorMessage += "Derivate:" + derivateError + " ";
				if (resultError != null) errorMessage += "Result:" + resultError + " ";
				return errorMessage;
			}
		}
		else { // -------- Error Position ----------
			return errorPos;
		}
	}
	
	public inline function bindValuesToFormulaParams(formula:Formula) {
		var i = 1;
		while (i < inputs.length)
		{
			if (inputs[i+1].get() != null)
			{
				if (Std.isOfType(inputs[i+1].get(), Float)) {
					// trace ("Float param")
					formula.bind( (inputs[i+1].get():Float), inputs[i].get() );
				}
				else if (Std.isOfType(inputs[i+1].get(), String)) {
					// trace ("String param")
					formula.bind( (inputs[i+1].get():String), inputs[i].get() );
				}
				else {
					// trace ("Formula param")
					formula.bind( (inputs[i+1].get():Formula), inputs[i].get() );
				}
			}
			i+=2;
		}
	
	}
}
