package armory.logicnode;

class ProbabilisticOutputNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {

		var probs: Array<Float> = [];
		var probs_acum: Array<Float> = [];
		var sum: Float = 0;

		for (p in 1...inputs.length){
			probs.push(inputs[p].get());
			sum += probs[p-1];
		}

		if (sum > 1){
			trace(sum);
			for (p in 0...probs.length)
				probs[p] /= sum;
		}

		sum = 0;
		for (p in 0...probs.length){
			sum += probs[p];
			probs_acum.push(sum);
		}

		var rand: Float = Math.random();

		for (p in 0...probs.length){
			if (p == 0 && rand <= probs_acum[p]){ runOutput(p); break; }
			else if (0 < p && p < probs.length-1 && probs_acum[p-1] < rand && rand <= probs_acum[p]){ runOutput(p); break; }
			else if (p == probs.length-1 && probs_acum[p-1] < rand){ runOutput(p); break; }
		}
	}
}
