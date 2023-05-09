package armory.logicnode;
import haxe.io.Bytes;
import haxe.io.BytesInput;
import haxe.io.BytesOutput;

/**
 * extending TermNode with various math operations transformation and more.
 * by Sylvio Sell, Rostock 2017
 * 
 **/

class TermTransform {

	static var newOperation:String->?TermNode->?TermNode->TermNode = TermNode.newOperation;
	static var newValue:Float->TermNode = TermNode.newValue;
	
	/*
	 * Simplify: trims the length of a math expression
	 * 
	 */
	static public inline function simplify(t:TermNode):TermNode {
		var tnew:TermNode = t.copy();
		_simplify(tnew);
		return tnew;
	}
	
	static inline function _simplify(t:TermNode):Void {
		_expand(t);
		
		var len:Int = -1;
		var len_old:Int = 0;
		while (len != len_old) {
			if (t.isName && t.left != null) {
				simplifyStep(t.left);
			}
			else {
				simplifyStep(t);
			}
			len_old = len;
			len = t.length();
		}
	}
	
	// TODO: removing this calls in subfunctions could be better to understand algorithms-recursions !!!
	static function isEqualAfterSimplify(t1:TermNode, t2:TermNode):Bool {
		// ----> take care, _simplify changes both TermNodes on call !!!
		_simplify(t1);
		_simplify(t2);
		return t1.isEqual(t2, false, true);
	}
	
	static function simplifyStep(t:TermNode):Void {	
		if (!t.isOperation) return;
		
		if (t.left != null) {
			if (t.left.isValue) {
				if (t.right == null) {
					// setValue(result); // calculate operation with one value
					return;
				}
				else if (t.right.isValue) {
					t.setValue(t.result); // calculate result of operation with values on both sides
					return;
				}
			}
		}

		switch(t.symbol) {
			case '+':
				if (t.left.isValue && t.left.value == 0) t.copyNodeFrom(t.right);       // 0+a -> a
				else if (t.right.isValue && t.right.value == 0) t.copyNodeFrom(t.left); // a+0 -> a
				else if (t.left.symbol == 'ln' && t.right.symbol == 'ln') {             // ln(a)+ln(b) -> ln(a*b)
					t.setOperation('ln',
						newOperation('*', t.left.left.copy(), t.right.left.copy())
					);
				}                                         
				else if (t.left.symbol == '/' && t.right.symbol == '/' && isEqualAfterSimplify(t.left.right, t.right.right)) {
					t.setOperation('/',                                                 // a/b+c/b -> (a+c)/b
						newOperation('+', t.left.left.copy(), t.right.left.copy()),
						t.left.right.copy()
					);
				}
				else if (t.left.symbol == '/' && t.right.symbol == '/') {               // a/b+c/d -> (a*d+c*b)/(b*d)
					t.setOperation('/',
						newOperation('+',
							newOperation('*', t.left.left.copy(), t.right.right.copy()),
							newOperation('*', t.right.left.copy(), t.left.right.copy())
						),
						newOperation('*', t.left.right.copy(), t.right.right.copy())
					);
				}
				arrangeAddition(t);
				if(t.symbol == '+') {
					_factorize(t);
				}

			case '-':
				if (t.right.isValue && t.right.value == 0) t.copyNodeFrom(t.left);  // a-0 -> a
				else if (t.left.symbol == 'ln' && t.right.symbol == 'ln') {         // ln(a)-ln(b) -> ln(a/b)
					t.setOperation('ln',
						newOperation('/', t.left.left.copy(), t.right.left.copy())
					);
				}
				else if (t.left.symbol == '/' && t.right.symbol == '/' && isEqualAfterSimplify(t.left.right, t.right.right)) {
					t.setOperation('/',                                             // a/b-c/b -> (a-c)/b
						newOperation('-', t.left.left.copy(), t.right.left.copy()),
						t.left.right.copy()
					);
				}
				else if (t.left.symbol == '/' && t.right.symbol == '/') {           //a/b-c/d -> (a*d-c*b)/(b*d)
					t.setOperation('/', 
						newOperation('-',
							newOperation('*', t.left.left.copy(), t.right.right.copy()),
							newOperation('*', t.right.left.copy(), t.left.right.copy())
						),
						newOperation('*', t.left.right.copy(), t.right.right.copy())
					);
				}
				arrangeAddition(t);
				if(t.symbol == '-') {
					_factorize(t);
				}

			case '*':
				if (t.left.isValue) {
					if (t.left.value == 1) t.copyNodeFrom(t.right); // 1*a -> a
					else if (t.left.value == 0) t.setValue(0);      // 0*a -> 0
				}
				else if (t.right.isValue) {
					if (t.right.value == 1) t.copyNodeFrom(t.left); // a*1 -> a
					else if (t.right.value == 0) t.setValue(0);     // a*0 -> a
				}
				else if (t.left.symbol == '/') {                    // (a/b)*c -> (a*c)/b
					t.setOperation('/',
						newOperation('*', t.right.copy(), t.left.left.copy()),
						t.left.right.copy()
					);
				}
				else if (t.right.symbol == '/') {                   // a*(b/c) -> (a*b)/c
					t.setOperation('/',
						newOperation('*', t.left.copy(), t.right.left.copy()),
						t.right.right.copy()
					);
				}
				else {
					arrangeMultiplication(t);
				}

		case '/':
				if (isEqualAfterSimplify(t.left, t.right)) {                 // x/x -> 1
					t.setValue(1);
				}
				else {
					if (t.left.isValue && t.left.value == 0) t.setValue(0);  // 0/a -> 0
					else if (t.right.symbol == '/') {
						t.setOperation('/',
							newOperation('*', t.right.right.copy(), t.left.copy()),
							t.right.left.copy()
						);
					} 
					else if (t.right.isValue && t.right.value == 1) t.copyNodeFrom(t.left); // a/1 -> a
					else if (t.left.symbol == '/') {                         // (1/x)/b -> 1/(x*b)
						t.setOperation('/', t.left.left.copy(),
							newOperation('*', t.left.right.copy(), t.right.copy())
						);
					}
					else if (t.right.symbol == '/') {                        // b/(1/x) -> b*x
						t.setOperation('/',
							newOperation('*', t.right.right.copy(), t.left.copy()),
							t.right.left.copy()
						);
					}
					else if (t.left.symbol == '-' && t.left.left.isValue && t.left.left.value == 0)
					{
						t.setOperation('-', newValue(0),
							newOperation('/', t.left.right.copy(), t.right.copy())
						);
					}
					else{ // a*b/b -> a
						simplifyfraction(t);
					}
				}

			case '^':
				if (t.left.isValue) {
					if (t.left.value == 1) t.setValue(1);           // 1^a -> 1
					else if (t.left.value == 0) t.setValue(0);      // 0^a -> 0
				} else if (t.right.isValue) {
					if (t.right.value == 1) t.copyNodeFrom(t.left); // a^1 -> a 
					else if (t.right.value == 0) t.setValue(1);     // a^0 -> 1
				}
				else if (t.left.symbol == '^') {                    // (a^b)^c -> a^(b*c)
					t.setOperation('^', t.left.left.copy(),
						newOperation('*', t.left.right.copy(), t.right.copy())
					);
				}

			case 'ln':
				if (t.left.symbol == 'e') t.setValue(1);
			case 'log':
				if (isEqualAfterSimplify(t.left, t.right)) {
					t.setValue(1);
				}
				else {
					t.setOperation('/',                             // log(a,b) -> ln(b)/ln(a)
						newOperation('ln', t.right.copy()),
						newOperation('ln', t.left.copy())
					);
				}
		}
		if (t.left != null) simplifyStep(t.left);
		if (t.right != null) simplifyStep(t.right);
	}
		
	/*
	 * put all subterms separated by * into an array
	 * 
	 */
	static function traverseMultiplication(t:TermNode, p:Array<TermNode>)
	{
		if (t.symbol != "*") {
			p.push(t);
		}
		else {
			traverseMultiplication(t.left, p);
			traverseMultiplication(t.right, p);
		}
	}
	
	/*
	 * build tree consisting of multiple * from array
	 * 
	 */
	static function traverseMultiplicationBack(t:TermNode, p:Array<TermNode>)
	{
		if (p.length > 2) {
			t.setOperation('*', newValue(1), p.pop());
			traverseMultiplicationBack(t.left, p);
		}
		else if (p.length == 2) {
			t.setOperation('*', p[0].copy(), p[1].copy());
			p.pop();
			p.pop();
		}
		else {
			t.set(p.pop());
		}
	}

	/*
	 * put all subterms separated by * into an array
	 *
	 */
	static function traverseAddition(t:TermNode, p:Array<TermNode>, ?negative:Bool=false)
	{
		if (t.symbol == "+" && negative == false) {
			traverseAddition(t.left, p);
			traverseAddition(t.right, p);
		}
		else if (t.symbol == "-" && negative == false) {
			traverseAddition(t.left, p);
			traverseAddition(t.right, p, true);
		}
		else if (t.symbol == "+" && negative == true) {
			traverseAddition(t.left, p, true);
			traverseAddition(t.right, p, true);
		}
		else if (t.symbol == "-" && negative == true) {
			traverseAddition(t.left, p, true);
			traverseAddition(t.right, p);
		}
		else if (negative == true && !t.isValue || negative == true && t.isValue && t.value != 0) {
			p.push(newOperation('-', newValue(0), t));
		}
		else if (!t.isValue || t.isValue && t.value != 0) {
			p.push(t);
		}
		return(p);
	}

	/*
	 * build tree consisting of multiple - and + from array
	 *
	 */
	static function traverseAdditionBack(t:TermNode, p:Array<TermNode>)
	{
		if(p.length > 1) {
			if (p[p.length-1].symbol == "-") {
				t.set(p.pop());
			}
			else {
				t.setOperation("+", newValue(0), p.pop());
			}	
			traverseAdditionBack(t.left, p);
		}
		else if(p.length == 1){
			t.set(p.pop());
		}
	}

	/*
	 * reduce a fraction 
	 * 
	 */
	static function simplifyfraction(t:TermNode)
	{
		var numerator:Array<TermNode> = new Array();
		traverseMultiplication(t.left, numerator);
		var denominator:Array<TermNode> = new Array();
		traverseMultiplication(t.right, denominator);
		for (n in numerator) {
			for (d in denominator) {
				if (isEqualAfterSimplify(n, d)) {
					numerator.remove(n);
					denominator.remove(d);
				}
			}
		}
		if (numerator.length > 1) {
			traverseMultiplicationBack(t.left, numerator);
		}
		else if (numerator.length == 1) {
			t.setOperation('/', numerator.pop(), newValue(1));
		}
		else if (numerator.length == 0) {
			t.left.setValue(1);
		}
		if (denominator.length > 1) {
			traverseMultiplicationBack(t.right, denominator);
		}
		else if (denominator.length == 1) {
			t.setOperation('/', t.left.copy(), denominator.pop());
		}
		else if (denominator.length == 0) {
			t.right.setValue(1);
		}
	}
	
	/*
	 * expands a mathmatical expression recursivly into a polynomial
	 *
	 */
	static public function expand(t:TermNode):TermNode {
		var tnew:TermNode = t.copy();
		_expand(tnew);
		return tnew;
	}
	
	static function _expand(t:TermNode):Void {
		
		var len:Int = -1;
		var len_old:Int = 0;
		while(len != len_old) {
			if (t.symbol == '*') {
				expandStep(t);
			}
			else {
				if(t.left != null) {
					_expand(t.left);
				}
				if(t.right != null) {
					_expand(t.right);
			
				}
			}
			len_old = len;
			len = t.length();
		}
	}

	/*
	 * expands a mathmatical expression into a polynomial -> use only if top symbol=*
	 * 
	 */
	static function expandStep(t:TermNode):Void
	{
		var left:TermNode = t.left;
		var right:TermNode = t.right;

		if (left.symbol == "+" || left.symbol == "-") {
			if (right.symbol == "+" || right.symbol == "-") {
				if (left.symbol == "+" && right.symbol == "+") { // (a+b)*(c+d)
					t.setOperation('+',
						newOperation('+',
							newOperation('*', left.left.copy(), right.left.copy()),
							newOperation('*', left.left.copy(), right.right.copy())
						),
						newOperation('+',
							newOperation('*', left.right.copy(), right.left.copy()),
							newOperation('*', left.right.copy(), right.right.copy())
						)
					);
				}	
				else if (left.symbol == "+" && right.symbol == "-") { // (a+b)*(c-d)
					t.setOperation('+',
						newOperation('-',
							newOperation('*', left.left.copy(), right.left.copy()),
							newOperation('*', left.left.copy(), right.right.copy())
						),
						newOperation('-',
							newOperation('*', left.right.copy(), right.left.copy()),
							newOperation('*', left.right.copy(), right.right.copy())
						)
					);
				}
				else if (left.symbol == "-" && right.symbol == "+") { // (a-b)*(c+d)
					t.setOperation('-',
						newOperation('+',
							newOperation('*', left.left.copy(), right.left.copy()),
							newOperation('*', left.left.copy(), right.right.copy())
						),
						newOperation('+',
							newOperation('*', left.right.copy(), right.left.copy()),
							newOperation('*', left.right.copy(), right.right.copy())
						)
					);
				}
				else if (left.symbol == "-" && right.symbol == "-") { // (a-b)*(c-d)
					t.setOperation('-',
						newOperation('-',
							newOperation('*', left.left.copy(), right.left.copy()),
							newOperation('*', left.left.copy(), right.right.copy())
						),
						newOperation('-',
							newOperation('*', left.right.copy(), right.left.copy()),
							newOperation('*', left.right.copy(), right.right.copy())
						)
					);	
				}
			}
			else
			{
				if (left.symbol == "+") { // (a+b)*c
					t.setOperation('+',
						newOperation('*', left.left.copy(), right.copy()),
						newOperation('*', left.right.copy(), right.copy())
					);
				}
				else if (left.symbol == "-") { // (a-b)*c
					t.setOperation('-',
						newOperation('*', left.left.copy(), right.copy()),
						newOperation('*', left.right.copy(), right.copy())
					);
				}
			}
		}
		else if (right.symbol == "+" || right.symbol == "-") {
			if (right.symbol == "+") { // a*(b+c)
				t.setOperation('+',
					newOperation('*', left.copy(), right.left.copy()),
					newOperation('*', left.copy(), right.right.copy())
				);
			}
			else if (right.symbol == "-") { // a*(b-c)
				t.setOperation('-',
					newOperation('*', left.copy(), right.left.copy()),
					newOperation('*', left.copy(), right.right.copy())
				);
			}
		}
	}

	/*
	 * factorize a term: a*c+a*b -> a*(c+b)
	 *
	 */
	static public function factorize(t:TermNode):TermNode {
		var tnew:TermNode = t.copy();
		_factorize(tnew);
		return tnew;
	}
	
	static function _factorize(t:TermNode):Void {
	  	var mult_matrix:Array<Array<TermNode>> = new Array();
	 	var add:Array<TermNode> = new Array();
		
		// build matrix - addition in columns - multiplication in rows 
		traverseAddition(t, add);
		var add_length_old:Int = 0;
		for(i in add) {
			if(i.symbol == "-") {
				mult_matrix.push(new Array());
				traverseMultiplication(add[mult_matrix.length-1].right, mult_matrix[mult_matrix.length-1]);
			}
			else {
				mult_matrix.push(new Array());
				traverseMultiplication(add[mult_matrix.length-1], mult_matrix[mult_matrix.length-1]);
			}
		}
		
		// find and extract common factors
		var part_of_all:Array<TermNode> = new Array();
		factorize_extract_common(mult_matrix, part_of_all);
		if(part_of_all.length != 0) {
			var new_add:Array<TermNode> = new Array();
			var helper:TermNode = new TermNode();
			for(i in mult_matrix) {
				traverseMultiplicationBack(helper, i);
				var v:TermNode = new TermNode();
				v.set(helper);
				new_add.push(v);
			}
			for(i in 0...add.length) {
				if(add[i].symbol == '-' && add[i].left.value == 0) {
					new_add[i].setOperation('-', newValue(0), new_add[i].copy());
				}
			}

			t.setOperation('*', new TermNode(), new TermNode());
			traverseMultiplicationBack(t.left, part_of_all);
			traverseAdditionBack(t.right, new_add);
		}
	}
	
	// delete common factors of mult_matrix and add them to part_of_all	
	static function factorize_extract_common(mult_matrix:Array<Array<TermNode>>, part_of_all:Array<TermNode>):Void {
		var bool:Bool = false;
		var matrix_length_old:Int = -1;
		var i:TermNode=new TermNode();
		var exponentiation_counter:Int = 0;
		while(matrix_length_old != mult_matrix[0].length) {
			matrix_length_old = mult_matrix[0].length;
			for(p in mult_matrix[0]) {
				if(p.symbol == '^') {
					i.set(p.left);
					exponentiation_counter++;
				}
				else if(p.symbol == '-' && p.left.isValue && p.left.value == 0) {
					i.set(p.right);
				}
				else {
					i.set(p);
				}
				for(j in 1...mult_matrix.length) {
					bool = false;
					for(h in mult_matrix[j]) {
						if(isEqualAfterSimplify(h, i)) {
							bool = true;
							break;
						}
						else if(h.symbol == '^' && isEqualAfterSimplify(h.left , i)) {
							bool=true;
							exponentiation_counter++;
							break;
		
						}
						else if(h.symbol == '-' && h.left.isValue && h.left.value == 0 && isEqualAfterSimplify(h.right, i)) {
							bool=true;
							break;		
						}
					}
					if(bool == false) {
						break;
					}
				}
				if(bool == true && exponentiation_counter < mult_matrix.length) {
					part_of_all.push(new TermNode());
					part_of_all[part_of_all.length-1].set(i);
					var helper:TermNode = new TermNode();
					helper.set(i);
					delete_last_from_matrix(mult_matrix, helper);
					break;
				}
			}
		}
	}
	
	// deletes d from every row in mult_matrix once
	static function delete_last_from_matrix(mult_matrix:Array<Array<TermNode>>, d:TermNode):Void {
		for(i in mult_matrix) {
			if(i.length>1) {
				for(j in 1...i.length+1) {
					if(isEqualAfterSimplify(i[i.length-j], d)) { // a*x -> a
						for(h in 0...j-1) {
							i[i.length-j+h].set(i[i.length-j+h+1]);
						}
						i.pop();
						break;
					}
					else if(i[i.length-j].symbol == '^' && isEqualAfterSimplify(i[i.length-j].left, d)) { // x^n -> x^(n-1)
						i[i.length-j].right.set(newOperation('-', i[i.length-j].right.copy(), newValue(1)));
						break;
					}
					else if(i[i.length-j].symbol == '-' && i[i.length-j].left.isValue && i[i.length-j].left.value == 0 && isEqualAfterSimplify(i[i.length-j].right, d)) {
					       i[i.length-j].right.set(newValue(1));
				       		break;
					}		
				}
			}
			else if(i[0].symbol == '^' && isEqualAfterSimplify(i[0].left, d)) { // x^n -> x^(n-1)
				i[0].right.set(newOperation('-', i[0].right.copy(), newValue(1)));
			}
			else {
				i[0].set(newValue(1));
			}
		}
	}
	
	// compare function for Array.sort()
	static function formsort_compare(t1:TermNode, t2:TermNode):Int
	{	
		if (formsort_priority(t1) > formsort_priority(t2)) {
			return -1;
		}
		else if (formsort_priority(t1) < formsort_priority(t2)) {
			return 1;
		}
		else{
			if (t1.isValue && t2.isValue) {
				if (t1.value >= t2.value) {
					return(-1);
				}
				else{
					return(1);
				}
			}
			else if (t1.isOperation && t2.isOperation) {
				if(t1.right != null && t2.right != null) {
					return(formsort_compare(t1.right, t2.right));
				}
				else {
					return(formsort_compare(t1.left, t2.left));
				}
			}
			else return 0;
		}
	}

	// priority function for formsort_compare()
	static function formsort_priority(t:TermNode):Float
	{	
		return switch(t.symbol)
		{
			case s if (t.isParam): t.symbol.charCodeAt(0);
			case s if (t.isName):  t.symbol.charCodeAt(0);
			case s if (t.isValue): 1+0.00001*t.value;
			case s if (TermNode.twoSideOpRegFull.match(s)) : 
				if(t.symbol == '-' && t.left.value == 0) {
					formsort_priority(t.right);
				}
				else {													 
					formsort_priority(t.left)+formsort_priority(t.right)*0.001;
				}
			case s if (TermNode.oneParamOpRegFull.match(s)): -5 - TermNode.oneParamOp.indexOf(s);
			case s if (TermNode.twoParamOpRegFull.match(s)): -5 - TermNode.oneParamOp.length - TermNode.twoParamOp.indexOf(s);
			case s if (TermNode.constantOpRegFull.match(s)): -5 - TermNode.oneParamOp.length - TermNode.twoParamOp.length - TermNode.constantOp.indexOf(s);
			
			default: -5 - TermNode.oneParamOp.length - TermNode.twoParamOp.length - TermNode.constantOp.length;
		}
	}

	/*
	 * sort a Tree consisting of products
	 * 
	 */
	static function arrangeMultiplication(t:TermNode):Void
	{
		var mult:Array<TermNode> = new Array();
		traverseMultiplication(t, mult);
		mult.sort(formsort_compare);
		traverseMultiplicationBack(t, mult);
	}

	/*
	 * sort a Tree consisting of addition and subtraction
	 *
	 */
	static function arrangeAddition(t:TermNode):Void
	{
		var addlength_old:Int = -1;
		var add:Array<TermNode> = new Array();
		traverseAddition(t, add);
		add.sort(formsort_compare);
		while(add.length != addlength_old) {
			addlength_old = add.length;
			for(i in 0...add.length-1) {
				if(isEqualAfterSimplify(add[i], add[i+1])) {
					add[i].setOperation('*', add[i].copy(), newValue(2));
					for(j in 1...add.length-i-1) {
						add[i+j] = add[i+j+1];
					}
					add.pop();
					break;
				}
				if(add[i].symbol == '*' && add[i+1].symbol == '*' && add[i].right.isValue && add[i+1].right.isValue && isEqualAfterSimplify(add[i].left, add[i+1].left)) {
					add[i].right.setValue(add[i].right.value+add[i+1].right.value);
					for(j in 1...add.length-i-1) {
						add[i+j] = add[i+j+1];
					}
					add.pop();
					break;
				}
				if(add[i].isValue && add[i+1].isValue) {
					add[i].setValue(add[i].value+add[i+1].value);
					for(j in 1...add.length-i-1) {
						add[i+j] = add[i+j+1];
					}
					add.pop();
					break;
				}
				if((add[i].symbol == '-' && add[i].left.isValue && add[i].left.value == 0 && isEqualAfterSimplify(add[i].right, add[i+1])) || (add[i+1].symbol == '-' && add[i+1].left.isValue && add[i+1].left.value == 0 && isEqualAfterSimplify(add[i+1].right, add[i]))) {
					for(j in 0...add.length-i-2) {
						add[i+j] = add[i+j+2];
					}
					add.pop();
					add.pop();
					if(add.length == 0){
						add.push(newValue(0));
					}
					break;
				}
			}

			if(add[0].symbol == '-' && add[0].left.value == 0) {
				for(i in add) {
					if(i.symbol == '-' && i.left.value == 0) {
						i.set(i.right);
					}
					else {
						i.setOperation('-', newValue(0), i.copy());
					}
				}
				t.setOperation('-', newValue(0), new TermNode());
				traverseAdditionBack(t.right, add);
				return;
			}
				
		}
		traverseAdditionBack(t, add);
	}	
}

/**
 * symbolic derivation
 * by Sylvio Sell, Rostock 2017
 * 
 **/

class TermDerivate {

	static var newOperation:String->?TermNode->?TermNode->TermNode = TermNode.newOperation;
	static var newValue:Float->TermNode = TermNode.newValue;

	/*
	 * creates a new term that is derivate of a given term 
	 * 
	 */
	static public inline function derivate(t:TermNode, p:String):TermNode {	
		return switch (t.symbol) 
		{
			case s if (t.isName): TermNode.newName( t.symbol, derivate(t.left, p) );
			case s if (t.isValue || TermNode.constantOpRegFull.match(s)): newValue(0);
			case s if (t.isParam): (t.symbol == p) ? newValue(1) : newValue(0);
			case '+' | '-':
				newOperation(t.symbol, derivate(t.left, p), derivate(t.right, p));
			case '*':
				newOperation('+',
					newOperation('*', derivate(t.left, p), t.right.copy()),
					newOperation('*', t.left.copy(), derivate(t.right, p))
				);
			case '/':
				newOperation('/',
					newOperation('-',
						newOperation('*', derivate(t.left, p), t.right.copy()),
						newOperation('*', t.left.copy(), derivate(t.right, p))
					),
					newOperation('^', t.right.copy(), newValue(2) )
				);
			case '^':
				if (t.left.symbol == 'e')
					newOperation('*', derivate(t.right, p),
						newOperation('^', newOperation('e'), t.left.copy())
					);
				else
					newOperation('*', 
						newOperation('^', t.left.copy(), t.right.copy()),
						newOperation('*',
							t.right.copy(),
							newOperation('ln', t.left.copy())
						).derivate(p)
					);
			case 'sin':
				newOperation('*', derivate(t.left, p),
					newOperation('cos', t.left.copy())
				);
			case 'cos':
				newOperation('*', derivate(t.left, p),
					newOperation('-', newValue(0),
						newOperation('sin', t.left.copy() )
					)
				);
			case 'tan':
				newOperation('*', derivate(t.left, p),
					newOperation('+', newValue(1),
						newOperation('^',
							newOperation('tan', t.left.copy() ),
							newValue(2)
						)
					)
				);
			case 'cot':
				newOperation('/',
					newValue(1),
					newOperation('tan', t.left.copy())
				).derivate(p);				
			case 'atan':
				newOperation('*', derivate(t.left, p),
					newOperation('/', newValue(1),
						newOperation('+', newValue(1),
							newOperation('^', t.left.copy(), newValue(2))
						)
					)
				);
			case 'atan2':
				newOperation('/', 
					newOperation('-',
						newOperation('*', t.right.copy(), derivate(t.left, p)),
						newOperation('*', t.left.copy(), derivate(t.right, p))
					),
					newOperation('+',
						newOperation('*', t.left.copy(), t.left.copy()),
						newOperation('*', t.right.copy(), t.right.copy())
					)
				);
			case 'asin':
				newOperation('*', derivate(t.left, p),
					newOperation('/', newValue(1),
						newOperation('^',
							newOperation('-', newValue(1),
								newOperation('^', t.left.copy(), newValue(2))
							), newOperation('/', newValue(1), newValue(2))
						)
					)
				);
			case 'acos':
				newOperation('*', derivate(t.left, p),
					newOperation('-', newValue(0),
						newOperation('/', newValue(1),
							newOperation('^',
								newOperation('-', newValue(1),
									newOperation('^', t.left.copy(), newValue(2))
								), newOperation('/', newValue(1), newValue(2))
							)
						)
					)
				);
			case 'log':
				newOperation('/',
					newOperation('ln', t.right.copy()),
					newOperation('ln', t.left.copy())
				).derivate(p);
			case 'ln':
				newOperation('*', derivate(t.left, p),
					newOperation('/', newValue(1), t.left.copy())
				);
			case 'abs':
				newOperation('*', derivate(t.left, p),
					newOperation('/', t.left.copy(), newOperation('abs', t.left.copy()) )
				);
				
			default: throw('derivation of "${t.symbol}" not implemented');	
		}

	}
}

/**
 * knot of a Tree to do math operations at runtime
 * by Sylvio Sell, Rostock 2017
 * 
 **/
	
typedef OperationNode = {symbol:String, left:TermNode, right:TermNode, leftOperation:OperationNode, rightOperation:OperationNode, precedence:Int};

class TermNode {

	/*
	 * Properties
	 * 
	 */
	var operation:TermNode->Float; // operation function pointer
	public var symbol:String; //operator like "+" or parameter name like "x"

	public var left:TermNode;  // left branch of tree
	public var right:TermNode; // right branch of tree
	
	public var value:Float;  // leaf of the tree
	
	public var name(get, set):String;  // name is stored into a param-TermNode at root of the tree
	inline function get_name():String return (isName) ? symbol : null;
	public static inline function checkValidName(name:String) if (!nameRegFull.match(name)) throw('Not allowed characters for name $name".');
	inline function set_name(name:String):String {
		if (name == null && isName) {
			copyNodeFrom(left);
		}
		else {
			//if (!nameRegFull.match(name)) throw('Not allowed characters for name $name".');
			checkValidName(name);
			if (isName) symbol = name else setName(name, copyNode());
		}
		return name;
	}
	
	/*
	 * returns depth of parameter bindings
	 * 
	 */	
	public inline function depth():Int {
		if (isName && left != null) return left._depth();
		else return _depth();
	}
	public inline function _depth():Int {
		var l:Int = 0;
		var r:Int = 0;
		var d:Int = 0;
		if (isParam) {
			if (left == null) d = 0;
			else if (!left.isName) d = 1;
		}
		else if (isName) d = 1; 
		
		if (left != null) l = left._depth();
		if (right != null) r = right._depth();
		
		return( d + ((l>r) ? l : r));
	}
	
	
	/*
	 * Check Type of TermNode
	 * 
	 */
	public var isName(get, null):Bool; // true -> root TermNode that holds name
	inline function get_isName():Bool return Reflect.compareMethods(operation, opName);
	
	public var isParam(get, null):Bool; // true -> it's a parameter
	inline function get_isParam():Bool return Reflect.compareMethods(operation, opParam);
	
	public var isValue(get, null):Bool; // true ->  it's a value (no left and right)
	inline function get_isValue():Bool return Reflect.compareMethods(operation, opValue);
	
	public var isOperation(get, null):Bool; // true ->  it's a operation TermNode
	inline function get_isOperation():Bool return !(isName||isParam||isValue);
	
	/*
	 * Calculates result of all Operations
	 * throws error if there is unbind param
	 */
	public var result(get, null):Float; // result of tree calculation
	inline function get_result():Float return operation(this);
	
	/*
	 * Constructors
	 * 
	 */
	public function new() {}
	
	public static inline function newName(name:String, ?term:TermNode):TermNode {
		var t:TermNode = new TermNode();
		t.setName(name, term);
		return t;
	}
	
	public static inline function newParam(name:String, ?term:TermNode):TermNode {
		var t:TermNode = new TermNode();
		t.setParam(name, term);
		return t;
	}
	
	public static inline function newValue(f:Float):TermNode {
		var t:TermNode = new TermNode();
		t.setValue(f);
		return t;
	}
	
	public static inline function newOperation(s:String, ?left:TermNode, ?right:TermNode):TermNode {
		var t:TermNode = new TermNode();
		t.setOperation(s, left, right);
		return t;
	}

	
	/*
	 * atomic methods
	 * 
	 */
	public inline function set(term:TermNode):TermNode {
		// TODO: new param to keep the existing bindings if there is same parameters
		if (isName) {
			if (!term.isName) left = term.copy();
			else if (term.left != null) left = term.left.copy();
			else left = null;
		}
		else {
			if (!term.isName) copyNodeFrom(term.copy());
			else if (term.left != null) copyNodeFrom(term.left.copy());
			//else return null; // TODO: check if that can ever been!
		}
		return this;
	}
	
	public inline function setName(name:String, ?term:TermNode) {
		operation = opName;
		symbol = name;
		left = term; right = null;
	}
	
	public inline function setParam(name:String, ?term:TermNode) {
		operation = opParam;
		symbol = name;
		left = term; right = null;
	}
	
	public inline function setValue(f:Float):Void {
		operation = opValue;
		symbol = null;
		value = f;
		left = null; right = null;
	}
	
	public inline function setOperation(s:String, ?left:TermNode, ?right:TermNode):Void {
		operation = MathOp.get(s);
		if (operation != null)
		{
			symbol = s;
			this.left = left;
			this.right = right;
		}
		else throw ('"$s" is no valid operation.');
	}

	/*
	 * returns an array of parameter-names
	 * 
	 */	
	public inline function params():Array<String> {
		var ret:Array<String> = new Array();
		if (isParam) {
			ret.push(symbol);
		}
		else {
			if (left != null ) {
				for (i in left.params()) if (ret.indexOf(i) < 0) ret.push(i);
			}
			if (right != null) {
				for (i in right.params()) if (ret.indexOf(i) < 0) ret.push(i);
			}
		}
		return ret;
	}
	
	/*
	 * check if term has a param
	 * 
	 */	
	public function hasParam(paramName:String):Bool {
		if (isParam && symbol == paramName) return true;
		if (left != null )
			if (left.hasParam(paramName)) return true;
		if (right != null)
			if (right.hasParam(paramName)) return true;
		return false;
	}
	
	
	/*
	 * bind terms to parameters
	 * 
	 */	
	public inline function bind(params:Map<String, TermNode>):TermNode {
		if (isParam) {
			if (params.exists(symbol)) left = params.get(symbol);
		}
		else {
			if (left != null) left.bind(params);
			if (right != null) right.bind(params);
		}
		return this;
	}
	
	
	/*
	 * unbind terms that is bind to parameter-names
	 * 
	 */	
	public inline function unbind(params:Array<String>):TermNode {
		if (isParam) {
			if (params.indexOf(symbol) >= 0) left = null;
		}
		else {
			if (left != null) left.unbind(params);
			if (right != null) right.unbind(params);
		}
		return this;
	}
	
	
	/*
	 * unbind terms
	 * 
	 */	
	public inline function unbindTerm(params:Array<TermNode>):TermNode {
		if (isParam) {
			if (left != null) {
				if (params.indexOf(left) >= 0) left = null;
			}
		}
		else {
			if (left != null) left.unbindTerm(params);
			if (right != null) right.unbindTerm(params);
		}		
		return this;
	}
	
	/*
	 * check if a term is binded to
	 * 
	 */	
	public function hasBinding(term:TermNode):Bool {
		if (isParam && left == term) return true;
		if (left != null)
			if (left.hasBinding(term)) return true;
		if (right != null)
			if (right.hasBinding(term)) return true;		
		return false;
	}
	
	/*
	 * unbind all terms that is bind to parameter-names
	 * 
	 */	
	public inline function unbindAll():TermNode {
		if (isParam) left = null;
		else {
			if (left != null) left.unbindAll();
			if (right != null) right.unbindAll();
		}
		return this;
	}	
	
	
	/*
	 * returns a new Term where all bindings are resolved down to
	 * the specified depth 
	 */
	public inline function resolveAll(depth:Int = -1):TermNode {
		// TODO: check better way
		if (isValue) return TermNode.newValue(value);
		else if (isName) return TermNode.newName(symbol, (left!=null) ? left.resolveAll(depth) : null);
		else if (isParam) {
			if (left == null) return TermNode.newParam(symbol, left);
			else if (depth == 0)
				return (left.isName) ? left.left : left;
			else if (depth > 0)
				return (left.isName) ? left.left.copy(depth).resolveAll(depth-1) : left.copy(depth).resolveAll(depth - 1);
			else 
				return (left.isName) ? left.left.resolveAll(depth - 1) : left.resolveAll(depth - 1);
		}
		else return TermNode.newOperation(symbol, (left!=null) ? left.resolveAll(depth) : null, (right!=null) ? right.resolveAll(depth) : null);
	}
	
	/*
	 * returns a recursive copy by starting with this TermNode
	 * depth can be used to define how deep it should copy the param-linked formulas
	 * 
	 */	
	public function copy(depth:Int = -1):TermNode
	{
		if (isValue) return TermNode.newValue(value);
		else if (isName) return TermNode.newName(symbol, (left!=null) ? left.copy(depth) : null);
		else if (isParam) return TermNode.newParam(symbol, (left!=null) ? ((depth == 0) ? left : left.copy(depth-1)) : null);
		else return TermNode.newOperation(symbol, (left!=null) ? left.copy(depth) : null, (right!=null) ? right.copy(depth) : null);
	}

	/*
	 * returns a clone of this TermNode only
	 * 
	 */	
	function copyNode():TermNode
	{
		if (isValue) return TermNode.newValue(value);
		else if (isName) return TermNode.newName(symbol, left);
		else if (isParam) return TermNode.newParam(symbol, left);
		else return TermNode.newOperation(symbol, left, right);
	}

	/*
	 * copy all from other TermNode to this
	 * 
	 */	
	public inline function copyNodeFrom(t:TermNode):Void {
		if (t.isValue) setValue(t.value);
		else if (t.isName) setName(t.symbol, t.left);
		else if (t.isParam) setParam(t.symbol, t.left);
		else setOperation(t.symbol, t.left, t.right);
	}
	
	
	/*
	 * number of TermNodes inside Tree
	 * 
	 */	
	public function length(?depth:Null<Int>=null):Int {
		if (depth == null) depth = -1;
		return switch(symbol) {
			case s if (isValue): 1;
			case s if (isName):  (left == null) ? 0 : left.length(depth);
			case s if (isParam): (depth == 0 || left == null) ? 1 : left.length(depth-1);
			case s if (constantOpRegFull.match(s)): 1;
			case s if (oneParamOpRegFull.match(s)): 1 + left.length(depth);
			default: 1 + left.length(depth) + right.length(depth);
		}		
	}
			
	
	/*
	 * returns true if other term is equal in data and structure
	 * 
	 */	
	public function isEqual(t:TermNode, ?compareNames=false, ?compareParams=false):Bool
	{
		if ( !compareNames && (isName || t.isName) ) {
			if (isName   && left   != null) return left.isEqual(t, compareNames, compareParams);
			if (t.isName && t.left != null) return isEqual(t.left, compareNames, compareParams);
			return (isName && t.isName);
		}
		
		if ( !compareParams && (isParam || t.isParam) ) {
			if (isParam   && left   != null) return left.isEqual(t, compareNames, compareParams);
			if (t.isParam && t.left != null) return isEqual(t.left, compareNames, compareParams);
			return (isParam && t.isParam);
		}
		
		var is_equal:Bool = false;
		
		if (isValue && t.isValue)
			is_equal = (value==t.value);
		else if ( (isName && t.isName) || (isParam && t.isParam) || (isOperation && t.isOperation) )
			is_equal = (symbol==t.symbol);
		
		if (left != null) {
			if (t.left != null) is_equal = is_equal && left.isEqual(t.left, compareNames, compareParams);
			else is_equal = false;
		}
		if (right != null) {
			if (t.right != null) is_equal = is_equal && right.isEqual(t.right, compareNames, compareParams);
			else is_equal = false;		
		}

		return is_equal;
	}
	
	/*
	 * static Function Pointers (to stored in this.operation)
	 * 
	 */		
	static function opName(t:TermNode) :Float if (t.left!=null) return t.left.result else throw('Empty function "${t.symbol}".');
	static function opParam(t:TermNode):Float if (t.left!=null) return t.left.result else throw('Missing parameter "${t.symbol}".');
	static function opValue(t:TermNode):Float return t.value;
	
	static var MathOp:Map<String, TermNode->Float> = [
		// two side operations
		"+"    => function(t) return t.left.result + t.right.result,
		"-"    => function(t) return t.left.result - t.right.result,
		"*"    => function(t) return t.left.result * t.right.result,
		"/"    => function(t) return t.left.result / t.right.result,
		"^"    => function(t) return Math.pow(t.left.result, t.right.result),
		"%"    => function(t) return t.left.result % t.right.result,
		
		// function without params (constants)
		"e"    => function(t) return Math.exp(1),
		"pi"   => function(t) return Math.PI,

		// function with one param
		"abs"  => function(t) return Math.abs(t.left.result),
		"ln"   => function(t) return Math.log(t.left.result),
		"sin"  => function(t) return Math.sin(t.left.result),
		"cos"  => function(t) return Math.cos(t.left.result),
		"tan"  => function(t) return Math.tan(t.left.result),
		"cot"  => function(t) return 1/Math.tan(t.left.result),
		"asin" => function(t) return Math.asin(t.left.result),
		"acos" => function(t) return Math.acos(t.left.result),
		"atan" => function(t) return Math.atan(t.left.result),
		
		// function with two params
		"atan2"=> function(t) return Math.atan2(t.left.result, t.right.result),
		"log"  => function(t) return Math.log(t.right.result) / Math.log(t.left.result),
		"max"  => function(t) return Math.max(t.left.result, t.right.result),
		"min"  => function(t) return Math.min(t.left.result, t.right.result),		
	];
	
	static var twoSideOp_ = "^,/,*,-,+,%";  // <- order here determines the operator precedence
	static var constantOp_ = "e,pi"; // functions without parameters like "e() or pi()"
	static var oneParamOp_ = "abs,ln,sin,cos,tan,cot,asin,acos,atan"; // functions with one parameter like "sin(2)"
	static var twoParamOp_ = "atan2,log,max,min";                 // functions with two parameters like "max(a,b)"

	static public var twoSideOp :Array<String> = twoSideOp_.split(',');
	static public var constantOp:Array<String> = constantOp_.split(',');
	static public var oneParamOp:Array<String> = oneParamOp_.split(',');
	static public var twoParamOp:Array<String> = twoParamOp_.split(',');
	
	static var precedence:Map<String,Int> = [ for (i in 0...twoSideOp.length) twoSideOp[i] => i ];
	

	
	/*
	 * Regular Expressions for parsing
	 * 
	 */	
	static var clearSpacesReg:EReg = ~/\s+/g;
	static var trailingSpacesReg:EReg = ~/^(\s+)/;
	
	static var numberReg:EReg = ~/^([-+]?\d+\.?\d*)/;
	static var paramReg:EReg = ~/^([a-z]+)/i;

	static var constantOpReg:EReg = new EReg("^(" + constantOp.join("|")  + ")\\(\\)" , "i");
	static var oneParamOpReg:EReg = new EReg("^(" + oneParamOp.join("|")  + ")\\(" , "i");
	static var twoParamOpReg:EReg = new EReg("^(" + twoParamOp.join("|")  + ")\\(" , "i");
	static var twoSideOpReg: EReg = new EReg("^(" + "\\"+ twoSideOp.join("|\\") + ")" , "");

	static public var constantOpRegFull:EReg = new EReg("^(" + constantOp.join("|")  + ")$" , "i");
	static public var oneParamOpRegFull:EReg = new EReg("^(" + oneParamOp.join("|")  + ")$" , "i");
	static public var twoParamOpRegFull:EReg = new EReg("^(" + twoParamOp.join("|")  + ")$" , "i");
	static public var twoSideOpRegFull: EReg = new EReg("^(" + "\\"+ twoSideOp.join("|\\") + ")$" , "");

	static var nameReg:EReg = ~/^([a-z]+)(\s*[:=]\s*)/i;
	static var nameRegFull:EReg = ~/^([a-z]+)$/i;
	
	static var signReg:EReg = ~/^([-+\s]+)/i;

	public static inline function trailingSpaces(s:String):Int {
		if (trailingSpacesReg.match(s)) return(trailingSpacesReg.matched(1).length);
		else return 0;
	}
	/*
	 * Build Tree up from String Math Expression
	 * 
	 */	
	public static inline function fromString(s:String, ?bindings:Map<String, TermNode>):TermNode {
		var errPos:Int = 0;
		errPos = trailingSpaces(s); s = s.substr(errPos);
		//s = clearSpacesReg.replace(s, ''); // clear all whitespaces
		if (nameReg.match(s)) {
			var name:String = nameReg.matched(1);
			s = s.substr(name.length + nameReg.matched(2).length);
			errPos += name.length + nameReg.matched(2).length;
			if (~/^\s*$/.match(s)) throw({"msg":"Can't parse Term from empty string.","pos":errPos});
			return newName(name, parseString(s, errPos, bindings));
		}
		if (~/^\s*$/.match(s)) throw({"msg":"Can't parse Term from empty string.","pos":errPos});
		return parseString(s, errPos, bindings);
	}
	
	static function parseString(s:String, errPos:Int, ?params:Map<String, TermNode>):TermNode {
		var t:TermNode = null;
		var operations:Array<OperationNode> = new Array();
		var e, f:String;
		var negate:Bool;
		var spaces:Int = 0;
		
		while (s.length != 0) // read in terms from left
		{
			negate = false;
			
			spaces = trailingSpaces(s); s = s.substr(spaces); errPos += spaces;
			
			if (numberReg.match(s)) {        // float number
				e = numberReg.matched(1);
				t = newValue(Std.parseFloat(e));
			}
			else if (constantOpReg.match(s)) {  // like e() or pi()
				e = constantOpReg.matched(1);
				t = newOperation(e);
				e+= "()";
			}
			else if (oneParamOpReg.match(s)) {  // like sin(...)
				f = oneParamOpReg.matched(1); errPos += f.length;
				s = "("+oneParamOpReg.matchedRight();
				e = getBrackets(s, errPos);
				t = newOperation(f, parseString(e.substring(1, e.length - 1), errPos+1, params) );
			}
			else if (twoParamOpReg.match(s)) { // like atan2(... , ...)
				f = twoParamOpReg.matched(1); errPos += f.length;
				s = "("+twoParamOpReg.matchedRight();
				e = getBrackets(s, errPos);
				var p1:String = e.substring(1, comataPos);
				var p2:String = e.substring(comataPos + 1, e.length - 1);
				if (comataPos == -1) throw({"msg":f+"() needs two parameter separated by comma.","pos":errPos});
				t = newOperation(f, parseString(p1, errPos+1, params), parseString(p2, errPos+1 + comataPos, params) );
			}
			else if (paramReg.match(s)) { // parameter
				e = paramReg.matched(1);
				t = newParam(e, (params==null) ? null : params.get(e));
			}
			else if (signReg.match(s)) { // start with +- 
				e = signReg.matched(1);
				s = s.substr(e.length); errPos += e.length;
				e = ~/[\s+]/g.replace(e, '');
				if (e.length % 2 > 0) {
					//s = "0-" + s;
					if (numberReg.match(s)) { // followed by float number
						e = numberReg.matched(1);
						t = newValue(-Std.parseFloat(e));
					} else {     // negative signed
						t = newValue(0); 
						s = "-" + s;
						e = "";
						negate = true;
					}
				} else continue; // positive signed
			}
			else if (twoSideOpReg.match(s)) { // start with other two side op 
				throw({"msg":"Missing left operand.","pos":errPos});
			}
			else {
				e = getBrackets(s, errPos);   // term inside brackets
				t = parseString(e.substring(1, e.length - 1), errPos+1, params);
			}
			
			s = s.substr(e.length); errPos += e.length;
			
			if (operations.length > 0) operations[operations.length - 1].right = t;

			spaces = trailingSpaces(s); s = s.substr(spaces); errPos += spaces;
			
			if (twoSideOpReg.match(s)) {   // two side operation symbol
				e = twoSideOpReg.matched(1); errPos += e.length;
				s = twoSideOpReg.matchedRight();
				spaces = trailingSpaces(s); s = s.substr(spaces); errPos += spaces;
				operations.push( { symbol:e, left:t, right:null, leftOperation:null, rightOperation:null, precedence:((negate) ? -1 :precedence.get(e)) } );
				if (operations.length > 1) {
					operations[operations.length - 2].rightOperation = operations[operations.length - 1];
					operations[operations.length - 1].leftOperation = operations[operations.length - 2];
				}
			} else if (s.length > 0) {
				if (s.indexOf(")") == 0) throw({"msg":"No opening bracket.","pos":errPos});
				if (!(s.indexOf("(") == 0 || numberReg.match(s) || paramReg.match(s) || constantOpReg.match(s) || oneParamOpReg.match(s) || twoParamOpReg.match(s)))
					throw({"msg":"Wrong char.","pos":errPos});
				else throw({"msg":"Missing operation.","pos":errPos});
			}
		}
		
		if ( operations.length > 0 ) {
			if ( operations[operations.length-1].right == null ) throw({"msg":"Missing right operand.","pos":errPos-spaces});
			else {
				operations.sort(function(a:OperationNode, b:OperationNode):Int
				{
					if (a.precedence < b.precedence) return -1;
					if (a.precedence > b.precedence) return 1;
					return 0;
				});
				for (op in operations) {
					t = TermNode.newOperation(op.symbol, op.left, op.right);
					if (op.leftOperation  != null && op.rightOperation != null) {
						op.rightOperation.leftOperation = op.leftOperation;
						op.leftOperation.rightOperation = op.rightOperation;
					}
					if (op.leftOperation  != null) op.leftOperation.right = t;
					if (op.rightOperation != null) op.rightOperation.left = t;
				}
				return t;
			}
		}
		else return t;
	}
	
	static var comataPos:Int;
	static function getBrackets(s:String, errPos:Int):String {
		var pos:Int = 1;
		if (s.indexOf("(") == 0) // check that s starts with opening bracket
		{
			if (~/^\(\s*\)/.match(s)) throw({"msg":"Empty brackets.", "pos":errPos});
			
			var i,j,k:Int;
			var openBrackets:Int = 1;
			comataPos = -1;
			while ( openBrackets > 0 )
			{	
				i = s.indexOf("(", pos);
				j = s.indexOf(")", pos);

				// check for commata position
				if (openBrackets == 1 && comataPos == -1) {
					k = s.indexOf(",", pos);
					if (k<j && j>0) comataPos = k;
				}
				
				if ((i>0 && j>0 && i<j)||(i>0 && j<0)) { // found open bracket
					openBrackets++; pos = i + 1;
				}
				else if ((j>0 && i>0 && j<i)||(j>0 && i<0)) { // found close bracket
					openBrackets--; pos = j + 1;
				} else { // no close or open found
					throw({"msg":"Wrong bracket nesting.","pos":errPos});
				}
			}
			return s.substring(0, pos);
		}
		if (s.indexOf(")") == 0) throw({"msg":"No opening bracket.", "pos":errPos});
		else throw({"msg":"Wrong char.","pos":errPos});
	}
	
	
	/*
	 * Puts out Math Expression as a String
	 * 
	 */
	public function toString(?depth:Null<Int> = null, ?plOut:String = null):String {
		var t:TermNode = this;
		if (isName) t = left;
		var options:Int;
		switch (plOut) {
			case 'glsl': options = noNeg|forceFloat|forcePow|forceMod|forceLog|forceAtan|forceConst;
			default:     options = 0;
		}
		return (left != null || !isName) ? t._toString(depth, options) : '';
	}
	// options
	public static inline var noNeg:Int = 1;
	public static inline var forceFloat:Int = 2;
	public static inline var forcePow:Int = 4;
	public static inline var forceMod:Int = 8;
	public static inline var forceLog:Int = 16;
	public static inline var forceAtan:Int = 32;
	public static inline var forceConst:Int = 64;
	
	inline function _toString(depth:Null<Int>, options:Int, ?isFirst:Bool=true):String {	
		if (depth == null) depth = -1;
		return switch(symbol) {
			case s if (isValue): floatToString(value, options);
			//case s if (isName && isFirst):  (left == null) ? symbol : left.toString(depth, false);
			case s if (isName):  (depth == 0 || left == null) ? symbol : left._toString(depth-1, options, false);
			case s if (isParam): (depth == 0 || left == null) ? symbol : left._toString(depth-((left.isName)?0:1), options, false);
			case s if (twoSideOpRegFull.match(s)) :
				if (symbol == "-" && left.isValue && left.value == 0 && options&noNeg == 0) symbol + right._toString(depth, options, false);
				else if (symbol == "^" && options&forcePow > 0) 'pow' + "(" + left._toString(depth, options) + "," + right._toString(depth, options) + ")";
				else if (symbol == "%" && options&forceMod > 0) 'mod' + "(" + left._toString(depth, options) + "," + right._toString(depth, options) + ")";
				else ((isFirst)?"":"(") + left._toString(depth, options, false) + symbol + right._toString(depth, options, false) + ((isFirst)?'':")");
			case s if (twoParamOpRegFull.match(s)):
				if (symbol == "log" && options&forceLog > 0) "(log(" + right._toString(depth, options) + ")/log(" + left._toString(depth, options) + "))";
				else if (symbol == "atan2" && options&forceAtan > 0) "atan(" + left._toString(depth, options) + "," + right._toString(depth, options) + ")";
				else symbol + "(" + left._toString(depth, options) + "," + right._toString(depth, options) + ")";
			case s if (constantOpRegFull.match(s)):
				if (symbol == "pi" && options & forceConst > 0) Std.string(Math.PI);
				else if (symbol == "e" && options&forceConst > 0) Std.string(Math.exp(1));
				else symbol + "()";
			default:
				if (symbol == "ln" && options&forceLog > 0) 'log' + "(" + left._toString(depth, options) + ")";
				else symbol + "(" + left._toString(depth, options) +  ")";
		}
	}
	
	inline function floatToString(value:Float, ?options:Int = 0):String {
		var s:String = Std.string(value);
		if (options&forceFloat > 0 && s.indexOf('.') == -1) s += ".0";
		return s;
	}
	
	/*
	 * enrolls terms and subterms for debugging
	 * 
	 */
	public function debug() {
		//TODO
		var out:String = "";// "(" + depth() + ")";
		for (i in 0 ... depth()+1) {
			if (i == 0) out += ((name != null) ? name : "?") + " = "; else out += " -> ";
			out += toString(i);
		}
		trace(out);
	}
	
	/*
	 * packs a TermNode and all sub-terms into Bytes
	 * 
	 */
	public function toBytes():Bytes {
		var b = new BytesOutput();
		_toBytes(b);
		return b.getBytes();
	}
	
	inline function _toBytes(b:BytesOutput) {
		// optimize (later to do): needs only 3 bit per TermNode type!
		if (isValue) {
			b.writeByte(0);
			b.writeFloat(value);
		}
		else if (isName) {
			b.writeByte((left!=null) ? 1:2);
			_writeString(symbol, b);
			if (left!=null) left._toBytes(b);
		}
		else if (isParam) {
			b.writeByte((left!=null) ? 3:4);
			_writeString(symbol, b);
			if (left!=null) left._toBytes(b);
		}
		else if (isOperation) {
			b.writeByte(5);
			var i:Int = twoSideOp.concat(constantOp.concat(oneParamOp.concat(twoParamOp))).indexOf(symbol);
			if (i > -1)	{
				b.writeByte(i);
				if (oneParamOpRegFull.match(symbol)) left._toBytes(b);
				else if (twoSideOpRegFull.match(symbol) || twoParamOpRegFull.match(symbol) ) { 
					left._toBytes(b);
					right._toBytes(b);
				}
			}
			else throw("Error in _toBytes");
		}
		else throw("Error in _toBytes");
	}
	
	inline function _writeString(s:String, b:BytesOutput):Void {
		b.writeByte((s.length<255) ? s.length: 255);
		for (i in 0...((s.length<255) ? s.length: 255)) b.writeByte(symbol.charCodeAt(i));
	}
	/*
	 * unserialize packed Bytes-Term to create a TermNode structure
	 * 
	 */
	public static function fromBytes(b:Bytes):TermNode {
		return _fromBytes(new BytesInput(b));	 
	}
	
	static inline function _fromBytes(b:BytesInput):TermNode {
		return switch (b.readByte()) {
			case 0: TermNode.newValue(b.readFloat());
			case 1: TermNode.newName( _readString(b), _fromBytes(b) );
			case 2: TermNode.newName( _readString(b) );
			case 3: TermNode.newParam( _readString(b), _fromBytes(b) );
			case 4: TermNode.newParam( _readString(b) );
			case 5: 
				var op:String = twoSideOp.concat(constantOp.concat(oneParamOp.concat(twoParamOp)))[b.readByte()];
				if (oneParamOpRegFull.match(op)) TermNode.newOperation( op, _fromBytes(b) );
				else if (twoSideOpRegFull.match(op) || twoParamOpRegFull.match(op) ) TermNode.newOperation( op, _fromBytes(b), _fromBytes(b) );
				else TermNode.newOperation( op );
			default: throw("Error in _fromBytes");
		}
	}
	
	static inline function _readString(b:BytesInput):String {
		var len:Int = b.readByte();
		var s:String = "";
		for (i in 0...len) s += String.fromCharCode(b.readByte());
		return s;
	}
	
	
	/**************************************************************************************
	 *                                                                                    *
	 * various math operations transformation and more.        *
	 *                                                                                    *
	 *                                                                                    *
	 **************************************************************************************/
	
	/*
	 * creates a new term that is derivate of a given term 
	 * 
	 */
	public function derivate(paramName:String):TermNode return TermDerivate.derivate(this, paramName);
	
	/*
	 * Simplify: trims the length of a math expression
	 * 
	 */
	public function simplify():TermNode return TermTransform.simplify(this);

	/*
	 * expands a mathmatical expression recursivly into a polynomial
	 * 
	 */
	public function expand():TermNode return TermTransform.expand(this);

	/*
	 * factorizes a mathmatical expression
	 *
	 */
	public function factorize():TermNode return TermTransform.factorize(this);
}

/**
 * abstract wrapper around TermNode
 * 
 * by Sylvio Sell, Rostock 2017
 */


@:forward( name, result, depth, params, hasParam, hasBinding, resolveAll, unbindAll, toBytes, debug, copy, derivate, simplify, expand, factorize)
abstract Formula(TermNode) from TermNode to TermNode
{	
    /**
        Creates a new formula from a String, e.g. new("1+2") or new("f: 1+2") where "f" is the name of formula
        @param  formulaString the String that representing the math expression
    **/
	inline public function new(formulaString:String) {
		this = TermNode.fromString(formulaString);
	}
	
    /**
        Copy all from another Formula to this (keeps the own name if it is defined)
		Keeps the bindings where this formula is linked into by a parameter.
        @param  formula the source formula from where the value is copyed
    **/
	public inline function set(formula:Formula):Formula return this.set(formula);

    /**
        Link a variable inside of this formula to another formula
        @param  formula formula that will be linked into
        @param  paramName (optional) name of the variable to link with (e.g. if formula have no or different name) 
    **/
	public function bind(formula:Formula, ?paramName:String):Formula {
		if (paramName != null) {
			TermNode.checkValidName(paramName);
			return this.bind( [paramName => formula] );
		}
		else {
			if (formula.name == null) throw 'Can\'t bind unnamed formula:"${formula.toString()}" as parameter.';
			return this.bind( [formula.name => formula] );
		}
	}
	
    /**
        Link variables inside of this formula to another formulas
        @param  formulas array of formulas to link to variables
        @param  paramNames (optional) names of the variables to link with (e.g. if formulas have no or different names) 
    **/
	public function bindArray(formulas:Array<Formula>, ?paramNames:Array<String>):Formula {
		var map = new Map<String, Formula>();
		if (paramNames != null) {
			if (paramNames.length != formulas.length) throw 'paramNames need to have the same length as formulas for bindArray().';
			for (i in 0...formulas.length) {
				TermNode.checkValidName(paramNames[i]);
				map.set(paramNames[i], formulas[i]);
			}
		}
		else {
			for (formula in formulas) {
				if (formula.name == null) throw 'Can\'t bind unnamed formula:"${formula.toString()}" as parameter.';
				map.set(formula.name, formula);
			} 
		}
		return this.bind(map);			
	}
	
    /**
        Link variables inside of this formula to another formulas
        @param  formulaMap map of formulas where the keys have same names as the variables to link with
    **/
	public inline function bindMap(formulaMap:Map<String, Formula>):Formula {
		return this.bind(formulaMap);
	}
	
	// ------------ unbind -------------
	
    /**
        Delete all connections of the linked formula
        @param  formula formula that has to be unlinked
    **/
	public inline function unbind(formula:Formula):Formula {
		return this.unbindTerm( [formula] );
	}
	
    /**
        Delete all connections of the linked formulas
        @param  formulas array of formulas that has to be unlinked
    **/
	public function unbindArray(formulas:Array<Formula>):Formula {
		return this.unbindTerm(formulas);
	}

    /**
        Delete all connections to linked formulas for a given variable name
        @param  paramName name of the variable where the connected formula has to unlink from
    **/
	public inline function unbindParam(paramName:String):Formula {
		TermNode.checkValidName(paramName);
		return this.unbind( [paramName] );
	}
	
    /**
        Delete all connections to linked formulas for the given variable names
        @param  paramNames array of variablenames where the connected formula has to unlink from
    **/
	public inline function unbindParamArray(paramNames:Array<String>):Formula {
		return this.unbind(paramNames);
	}

	// -----------------------------------

    /**
        Creates a new formula from a String, e.g. new("1+2") or new("f: 1+2") where "f" is the name of formula
        @param  depth (optional) how deep the variable-bindings should be resolved
        @param  plOut (optional) creates formula for a special language (only "glsl" at now)
    **/
	inline public function toString(?depth:Null<Int> = null, ?plOut:String = null):String return this.toString(depth, plOut);

    /**
        Creates a formula from a packet Bytes representation
    **/
	inline public static function fromBytes(b:Bytes):Formula return TermNode.fromBytes(b);
	
	@:to inline public function toStr():String return this.toString(0);
	@:to inline public function toFloat():Float return this.result;
	
	@:from static public function fromString(a:String):Formula return TermNode.fromString(a);
	@:from static public function fromFloat(a:Float):Formula return TermNode.newValue(a);

	static inline function twoSideOp(op:String, a:Formula, b:Formula ):Formula {
		return TermNode.newOperation( op,
			(a.name != null ) ? TermNode.newParam(a.name, a) : a,
			(b.name != null ) ? TermNode.newParam(b.name, b) : b 
		);
	}
	@:op(A + B) static public function add     (a:Formula, b:Formula):Formula return twoSideOp('+', a, b);
	@:op(A - B) static public function subtract(a:Formula, b:Formula):Formula return twoSideOp('-', a, b);
	@:op(A * B) static public function multiply(a:Formula, b:Formula):Formula return twoSideOp('*', a, b);
	@:op(A / B) static public function divide  (a:Formula, b:Formula):Formula return twoSideOp('/', a, b);
	@:op(A ^ B) static public function potenz  (a:Formula, b:Formula):Formula return twoSideOp('^', a, b);
	@:op(A % B) static public function modulo  (a:Formula, b:Formula):Formula return twoSideOp('%', a, b);

	public static inline function atan2(a:Formula, b:Formula):Formula return twoSideOp('atan2', a, b);
	public static inline function log  (a:Formula, b:Formula):Formula return twoSideOp('log',   a, b);
	public static inline function max  (a:Formula, b:Formula):Formula return twoSideOp('max',   a, b);
	public static inline function min  (a:Formula, b:Formula):Formula return twoSideOp('min',   a, b);

	static inline function oneParamOp(op:String, a:Formula):Formula {
		return TermNode.newOperation( op,
			(a.name != null ) ? TermNode.newParam(a.name, a) : a
		);
	}
	public static inline function abs (a:Formula):Formula return oneParamOp('abs', a);
	public static inline function ln  (a:Formula):Formula return oneParamOp('ln', a);
	public static inline function sin (a:Formula):Formula return oneParamOp('sin', a);
	public static inline function cos (a:Formula):Formula return oneParamOp('cos', a);
	public static inline function tan (a:Formula):Formula return oneParamOp('tan', a);
	public static inline function cot (a:Formula):Formula return oneParamOp('cot', a);
	public static inline function asin(a:Formula):Formula return oneParamOp('asin', a);
	public static inline function acos(a:Formula):Formula return oneParamOp('acos', a);
	public static inline function atan(a:Formula):Formula return oneParamOp('atan', a);
	
}

class MathExpressionNode extends LogicNode {

	public var property0: String; // Expression
	public var property1: Bool; // Clamp

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var r: Float = 0.0;
        var exp: String = property0;
        // Variable
        var a: Float = inputs[0].get();
        var b: Float = inputs[1].get();
        exp = StringTools.replace(exp, 'a', Std.string(a));
        exp = StringTools.replace(exp, 'b', Std.string(b));
        var c: Float = 0.0;
        var d: Float = 0.0;
        var e: Float = 0.0;
        var x: Float = 0.0;
        var y: Float = 0.0;
        var h: Float = 0.0;
        var i: Float = 0.0;
        var k: Float = 0.0;
        var i = 2;
        while (i < inputs.length) {
            switch (i) {
                case 2: 
                    c = inputs[i].get();
                    exp = StringTools.replace(exp, 'c', Std.string(c));
                case 3: 
                    d = inputs[i].get();
                    exp = StringTools.replace(exp, 'd', Std.string(d));
                case 4: 
                    e = inputs[i].get();
                    exp = StringTools.replace(exp, 'e', Std.string(e));
                case 5: 
                    x = inputs[i].get();
                    exp = StringTools.replace(exp, 'x', Std.string(x));
                case 6: 
                    y = inputs[i].get();
                    exp = StringTools.replace(exp, 'y', Std.string(y));
                case 7: 
                    h = inputs[i].get();
                    exp = StringTools.replace(exp, 'h', Std.string(h));
                case 8: 
                    i = inputs[i].get();
                    exp = StringTools.replace(exp, 'i', Std.string(i));
                case 9: 
                    k = inputs[i].get();
                    exp = StringTools.replace(exp, 'k', Std.string(k));
            }
            i++;
        }
        // Expression
        try {
            var f: Formula = new Formula(exp);
            r = f.result;
        } catch(msg: String) {
			#if arm_debug
            trace(msg);
			#end
        }
		// Clamp
		if (property1) r = r < 0.0 ? 0.0 : (r > 1.0 ? 1.0 : r);

		return r;
	}
}