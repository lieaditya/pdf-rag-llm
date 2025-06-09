"use client";

import SubmitQueryForm from "@/components/app/submitQueryForm";
import QueryList from "@/components/app/queryList";

export default function Home() {
  return (
		<>
			<SubmitQueryForm></SubmitQueryForm>
			<QueryList></QueryList>
		</>
  );
}
