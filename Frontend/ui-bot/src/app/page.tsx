import Image from "next/image";
import { ExpandableChatDemo } from "./signature/page";
import { ChatMessageListDemo } from "./board/page";

export default function Home() {
  return (
    <>  
    <div className="flex items-center justify-center  h-full">
      <div className="w-full max-w-2xl h-full p-4 flex flex-col">
        <ChatMessageListDemo />
      </div>
    </div>
    <ExpandableChatDemo />
    
    </>
  );
}
