import React, { createContext, useContext } from "react";

type UserContextType = {
	userId: string;
};

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ userId: string; children: React.ReactNode }> = ({ userId, children }) => {
	return <UserContext.Provider value={{ userId }}>{children}</UserContext.Provider>;
};

export function useUser() {
	const context = useContext(UserContext);
	if (!context) {
		throw new Error("useUser must be used within a UserProvider");
	}
	return context;
}
