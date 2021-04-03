package armory.system;

class FSM<T> {
	final transitions = new Array<Transition<T>>();
	final tempTransitions = new Array<Transition<T>>();
	var state: Null<State<T>>;
	var entered = false;

	public function new() {}

	public function bindTransition(canEnter: Void -> Bool, fromState: State<T>, toState: State<T>) {
		final transition = new Transition<T>(canEnter, fromState, toState);
		transitions.push(transition);
		syncTransitions();
	}

	public function setInitState(state: State<T>) {
		this.state = state;
		syncTransitions();
	}

	public function update() {
		if (!entered) {
			state.onEnter();
			entered = true;
		}

		state.onUpdate();

		for (transition in tempTransitions) {
			if (transition.canEnter()) {
				state.onExit();
				state = transition.toState;
				entered = false;
				syncTransitions();
				break;
			}
		}
	}

	public function syncTransitions() {
		tempTransitions.resize(0);

		for (transition in transitions) {
			if (transition.fromState == state) tempTransitions.push(transition);
		}
	}
}

class Transition<T> {
	public final canEnter: Void -> Bool;
	public final fromState: State<T>;
	public final toState: State<T>;

	public function new(canEnter: Void -> Bool, fromState: State<T>, toState: State<T>) {
		this.canEnter = canEnter;
		this.fromState = fromState;
		this.toState = toState;
	}
}

class State<T> {
	final owner: T;

	public function new(owner: T) {
		this.owner = owner;
	}

	public function onEnter() {}

	public function onUpdate() {}

	public function onExit() {}
}