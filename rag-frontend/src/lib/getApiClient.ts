"use client";

import { Configuration, DefaultApi } from "@/api-client";

export function getApiUrl() {
	return process.env.NEXT_PUBLIC_API_BASE_URL;
}

export default function createApiClient() {
	const apiConfig = new Configuration({
		basePath: getApiUrl(),		
	});
	const api = new DefaultApi(apiConfig);
	return api;
}
