package ai.langchain4j.assistant;

import dev.langchain4j.service.MemoryId;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.spring.AiService;
import reactor.core.publisher.Flux;

import static dev.langchain4j.service.spring.AiServiceWiringMode.EXPLICIT;

@AiService(
        wiringMode = EXPLICIT,
        streamingChatModel = "qwenStreamingChatModel",          // 改为流式输出
        chatMemoryProvider = "chatMemoryProviderXiaozhi"     // 配置记忆,实现记忆隔离，chatMemery和chatMemoryProvider保留其一即可
//        tools = "appointmentTools",                             //tools配置
//        contentRetriever = "contentRetrieverXiaozhiPincone"     //配置向量存储
)
public interface XiaozhiAgent {
    //    系统提示词
    @SystemMessage(fromResource = "zhaozhi-SysPrompt-Template.txt")
    Flux<String> chat(@MemoryId Long memoryId, @UserMessage String userMessage);
}

