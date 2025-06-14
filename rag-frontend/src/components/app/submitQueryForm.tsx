"use client";

import { useState } from "react";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import createApiClient from "@/lib/getApiClient";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { SubmitUserQueryUsersUserIdQueriesPostRequest } from "@/api-client";
import { useUser } from "@/context/UserContext";

export default function SubmitQueryForm() {
  const api = createApiClient();
	const { userId } = useUser();
  const originalPlaceHolder: string =
    "How to get six pack abs fast?";

  const [query, setQuery] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  const submitForm = () => {
    const queryToSubmit = query || originalPlaceHolder;
    console.log(`Submitting query: ${queryToSubmit}`);
    const request: SubmitUserQueryUsersUserIdQueriesPostRequest = {
			userId: userId,
			submitQueryRequest: {
				queryText: queryToSubmit,
			},
		};
    const response = api.submitUserQueryUsersUserIdQueriesPost(request);

    setIsSubmitting(true);
    response.then((data) => {
      console.log(data);
      router.push(`/viewQuery?query_id=${data.queryId}`);
    });
  };

  const textArea = (
    <Textarea
      placeholder={originalPlaceHolder}
      value={query}
      disabled={isSubmitting}
      onChange={(e) => {
        setQuery(e.currentTarget.value);
      }}
    />
  );

  const submitButton = (
    <Button onClick={submitForm} disabled={isSubmitting} className="ml-auto">
      {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />} Submit
    </Button>
  );

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Submit New Query</CardTitle>
        <CardDescription>
          Ask anything based on your uploaded PDFs.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="w-full">{textArea}</div>
      </CardContent>
      <CardFooter>{submitButton}</CardFooter>
    </Card>
  );
}
