"use client";

import { QueryModel } from "@/api-client";
import createApiClient from "@/lib/getApiClient";
import { useEffect, useState } from "react";
import QueryListItem from "./queryListItem";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Skeleton } from "../ui/skeleton";
import { useUser } from "@/context/UserContext";

export default function QueryList() {
  const api = createApiClient();
  const { userId } = useUser();

  const [isLoading, setIsLoading] = useState(true);
  const [queryItems, setQueryItems] = useState<QueryModel[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const request = {
          userId: userId,
        };
        const response = api.getUserQueriesUsersUserIdQueriesGet(request);
        response.then((data) => {
          console.log(data);
          setQueryItems(data);
          setIsLoading(false);
        });
        console.log(`Got data: ${response}`);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
    fetchData();
  }, []);

  let queryElements;
  if (isLoading) {
    queryElements = (
      <div className="space-y-2">
        <Skeleton className="h-6 w-full" />
        <Skeleton className="h-6 w-full" />
        <Skeleton className="h-6 w-full" />
      </div>
    );
  } else {
    queryElements = queryItems.map((queryItem) => {
      return <QueryListItem key={queryItem.queryId} {...queryItem} />;
    });
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Recent Queries</CardTitle>
        <CardDescription>
          Here are queries you&apos;ve recently submitted.
        </CardDescription>
      </CardHeader>
      <CardContent>{queryElements}</CardContent>
    </Card>
  );
}
