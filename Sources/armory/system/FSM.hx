package armory.system;

class FSM {
	var state: Null<State>;
	var nextState: Null<State>;
	var transitions = new Array<Transition>();
	var tempTransitions = new Array<Transition>();
	var entered = false;

	public function new() {}

	/**
	* Set the initial / current state of the FSM and return it
	* @param state The state to be set
	* @return State
	**/
	public function setState(state: State) {
		this.state = state;
		syncTransitions();
		return state;
	}

	/**
	* Bind multiple transitions to the specified state
	* @param canEnter The function that returns true or false to enter the transition
	* @param toState The next state the transiiton will return
	* @param fromStates The states that are allowed to be changed by the next state
	* @return Void
	**/
	public function bindTransitions(canEnter: Void -> Bool, toState: State, fromStates: Array<State>) {
		for (s in fromStates) {
			transitions.push(new Transition(canEnter, s, toState));
		}

		syncTransitions();
	}

	function syncTransitions() {
		tempTransitions = [];

		for (t in transitions) {
			if (t.isConnected(state)) tempTransitions.push(t);
		}
	}

	public function run() {
		if (!entered) {
			state.onEnter();
			entered = true;
		}

		state.onUpdate();

		for (t in tempTransitions) {
			if (t.canEnter()) {
				nextState = t.getNextState();
				state.onExit();
				state = nextState;
				entered = false;
				syncTransitions();
				break;
			}
		}
	}
}

class Transition {
	final func: Void -> Bool;
	final from: State;
	final to: State;

	public function new(func: Void -> Bool, from: State, to: State) {
		this.func = func;
		this.from = from;
		this.to = to;
	}

	public function canEnter() {
		return func();
	}

	public function isConnected(state: State) {
		return from == state;
	}

	public function getNextState() {
		return to;
	}
}

interface State {
	function onEnter(): Void;
	function onUpdate(): Void;
	function onExit(): Void;
}