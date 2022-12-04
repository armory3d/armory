package armory.network;

@:enum abstract OpCode(Int) {
	var Continuation = 0x00;
	var Text = 0x01;
	var Binary = 0x02;
	var Close = 0x08;
	var Ping = 0x09;
	var Pong = 0x0A;

	@:to public function toInt() {
		return this;
	}
}
