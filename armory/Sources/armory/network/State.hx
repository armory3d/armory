package armory.network;

enum State {
	Handshake;
	Head;
	HeadExtraLength;
	HeadExtraMask;
	Body;
	Closed;
}
