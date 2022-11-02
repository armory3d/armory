package armory.logicnode;

class GetDateTimeNode extends LogicNode {
	public var property0: String;
	public var value: Int;
	public var timeStamp: Float;
	public var timezoneOffset: Int;
	public var weekDay: Int;
	public var day: Int;
	public var month: Int;
	public var year: Int;
	public var hours: Int;
	public var minutes: Int;
	public var seconds: Int;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		if(property0 == "all"){
			var dateTime = Date.now();
			timeStamp = dateTime.getTime();
			timezoneOffset = dateTime.getTimezoneOffset();
			weekDay = dateTime.getDay();
			day = dateTime.getDate();
			month = dateTime.getMonth();
			year = dateTime.getFullYear();
			hours = dateTime.getHours();
			minutes = dateTime.getMinutes();
			seconds = dateTime.getSeconds();
			return switch (from) {
				case 0: timeStamp;
				case 1: timezoneOffset;
				case 2: weekDay;
				case 3: day;
				case 4: month;
				case 5: year;
				case 6: hours;
				case 7: minutes;
				case 8: seconds;
				default: null;
			}		
		} else if (property0 == "formatted"){
			return DateTools.format(Date.now(), inputs[0].get());
		} else {
			var dateTime = Date.now();
			return switch (property0) {
				case "now": dateTime;
				case "timestamp": dateTime.getTime();
				case "timezoneOffset": dateTime.getTimezoneOffset();
				case "weekDay": dateTime.getDay();
				case "day": dateTime.getDate();
				case "month": dateTime.getMonth();
				case "year": dateTime.getFullYear();
				case "hours": dateTime.getHours();
				case "minutes": dateTime.getMinutes();
				case "seconds": dateTime.getSeconds();
				default: null;
			}		
		}
	}
}
