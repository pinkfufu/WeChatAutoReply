package ai.langchain4j.bean;

import ai.langchain4j.store.MongoChatMemoryStore;
import dev.langchain4j.memory.chat.ChatMemoryProvider;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.rag.content.retriever.ContentRetriever;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import dev.langchain4j.store.embedding.EmbeddingStore;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.Collections;

@Configuration
public class XiaozhiAgentConfig {
    @Autowired
    private MongoChatMemoryStore mongoChatMemoryStore;
    @Autowired
    private EmbeddingStore embeddingStore;
    @Autowired
    private EmbeddingModel embeddingModel;

    @Bean
    ChatMemoryProvider chatMemoryProviderXiaozhi() {
        return memoryId -> MessageWindowChatMemory.builder()
                .id(memoryId)
                .chatMemoryStore(mongoChatMemoryStore)
                .maxMessages(500)
                .build();
    }

    @Bean
    ContentRetriever contentRetrieverXiaozhiPincone() {

        // [修改这里] 彻底断开与 Pinecone 的连接，返回一个空检索器，不花一分钱
        return query -> Collections.emptyList();
    }

/**
 * 暂时不用向量数据库了，直接返回一个空检索器，不花一分钱
 * 同时也注释掉 XiaozhiAgent中的检索器配置

 // 创建一个 EmbeddingStoreContentRetriever 对象，用于从嵌入存储中检索内容
 return EmbeddingStoreContentRetriever.builder()
 // 设置用于生成嵌入向量的嵌入模型
 .embeddingModel(embeddingModel)
 // 指定要使用的嵌入存储
 .embeddingStore(embeddingStore)
 // 设置最大检索结果数量，这里表示最多返回 1 条匹配结果
 .maxResults(1)
 // 设置最小得分阈值，只有得分大于等于 0.8 的结果才会被返回
 .minScore(0.8)
 // 构建最终的 EmbeddingStoreContentRetriever 实例
 .build();
 */
}



/*    @Bean
    ContentRetriever contentRetrieverXiaozhi() {
//使用FileSystemDocumentLoader读取指定目录下的知识库文档
//并使用默认的文档解析器对文档进行解析
        Document document1 = FileSystemDocumentLoader.loadDocument("D:\\Users\\ZhangYao\\Desktop\\课件\\资料\\knowledge\\医院信息.md");
        Document document2 = FileSystemDocumentLoader.loadDocument("D:\\Users\\ZhangYao\\Desktop\\课件\\资料\\knowledge\\科室信息.md");
        Document document3 = FileSystemDocumentLoader.loadDocument("D:\\Users\\ZhangYao\\Desktop\\课件\\资料\\knowledge\\神经内科.md");
        List<Document> documents = Arrays.asList(document1, document2, document3);
//使用内存向量存储
        InMemoryEmbeddingStore<TextSegment> embeddingStore = new InMemoryEmbeddingStore<>();
//使用默认的文档分割器
        EmbeddingStoreIngestor.ingest(documents, embeddingStore);
//从嵌入存储（EmbeddingStore）里检索和查询内容相关的信息
        return EmbeddingStoreContentRetriever.from(embeddingStore);
    }*/

