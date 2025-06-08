import { v4 as uuidv4 } from "uuid";

export function getSessionId() {
	if (typeof window === "undefined") {
		return "nobody";
	}

	let sessionId = sessionStorage.getItem("sessionId");
	if (!sessionId) {
		sessionId = uuidv4();
		sessionStorage.setItem("sessionId", sessionId);
	}

	return sessionId;
}
