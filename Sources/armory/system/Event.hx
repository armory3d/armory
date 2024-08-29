package armory.system;

import haxe.Constraints.Function;

/**
	Detailed documentation of the event system:
	[Armory Wiki: Events](https://github.com/armory3d/armory/wiki/events).
**/
class Event {

	static var events = new Map<String, Array<TEvent>>();

	/**
		Send an event with the given name to all corresponding listeners. This
		function directly executes the `onEvent` callbacks of those listeners.

		For an explanation of the `mask` value, please refer to the
		[wiki](https://github.com/armory3d/armory/wiki/events#event-masks).
	**/
	public static function send(name: String, mask = -1, ...args:Any) {
		var entries = get(name);
		if (entries != null) for (e in entries) if (mask == -1 || mask == e.mask ) Reflect.callMethod(e, e.onEvent, args);
	}

	/**
		Return the array of event listeners registered for events with the
		given name, or `null` if no listener is currently registered for the event.
	**/
	public static function get(name: String): Array<TEvent> {
		return events.get(name);
	}

	/**
		Add a listener to the event with the given name and return the
		corresponding listener object. The `onEvent` callback will be called
		when a matching event is sent.

		For an explanation of the `mask` value, please refer to the
		[wiki](https://github.com/armory3d/armory/wiki/events#event-masks).
	**/
	public static function add(name: String, onEvent: Function, mask = -1): TEvent {
		var e: TEvent = { name: name, onEvent: onEvent, mask: mask };
		var entries = events.get(name);
		if (entries != null) entries.push(e);
		else events.set(name, [e]);
		return e;
	}

	/**
		Remove _all_ listeners that listen to events with the given `name`.
	**/
	public static function remove(name: String) {
		events.remove(name);
	}

	/**
		Remove a specific listener. If the listener is not registered/added,
		this function does nothing.
	**/
	public static function removeListener(event: TEvent) {
		var entries = events.get(event.name);
		if (entries != null) {
			entries.remove(event);
			if (entries.length == 0) {
				events.remove(event.name);
			}
		}
	}
}

/**
	Represents an event listener.

	@see `armory.system.Event`
**/
typedef TEvent = {
	/** The name of the events this listener is listening to. **/
	var name: String;

	/** The callback function that is called when a matching event is sent. **/
	var onEvent: Function;

	/** The mask of the events this listener is listening to. **/
	var mask: Int;
}
