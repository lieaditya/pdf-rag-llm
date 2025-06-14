"use client";

import * as React from "react";
import { FileText } from "lucide-react";
import { UploaderProvider, UploadFn } from "../upload/uploader-provider";
import { FileUploader } from "../upload/multi-file";
import { useUser } from "@/context/UserContext";

export default function Sidebar() {
	const { userId } = useUser();

	const uploadFn: UploadFn = React.useCallback(
		async ({ file, onProgressChange, signal }) => {
			const response = await new Promise<{ url: string }>((resolve, reject) => {
				const xhr = new XMLHttpRequest();
				const url = process.env.NEXT_PUBLIC_API_BASE_URL + `users/${userId}/documents`;

				xhr.open('POST', url);

				xhr.upload.onprogress = (event) => {
					if (event.lengthComputable && onProgressChange) {
						const percent = (event.loaded / event.total) * 100;
						onProgressChange(percent);
					}
				};

				xhr.onload = () => {
					if (xhr.status >= 200 && xhr.status < 300) {
						try {
							resolve(JSON.parse(xhr.responseText));
						} catch {
							reject(new Error('Invalid JSON response'));
						}
					} else {
						reject(new Error(`Upload failed with status ${xhr.status}`));
					}
				};

				xhr.onerror = () => reject(new Error('Upload error'));
				xhr.onabort = () => reject(new DOMException('Upload aborted', 'AbortError'));

				if (signal) {
					signal.addEventListener('abort', () => xhr.abort());
				}

				const formData = new FormData();
				formData.append('documents', file);

				xhr.send(formData);
			});

			return response;
		}, []
	);

  return (
    <aside className="bg-white shadow-lg p-4 w-80 min-h-screen">
      <h2 className="font-bold mb-4 flex items-center text-gray-700">
        <FileText className="w-4 h-4 mr-2" /> Uploaded PDFs
      </h2>
			<UploaderProvider uploadFn={uploadFn} autoUpload>
				<FileUploader
					maxFiles={5}
					maxSize={1024 * 1024 * 2} // 2 MB
					accept={{
						'application/pdf': ['.pdf'],
					}}
				/>
			</UploaderProvider>
    </aside>
  );
}

