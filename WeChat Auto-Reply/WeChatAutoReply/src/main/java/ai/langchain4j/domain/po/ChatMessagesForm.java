package ai.langchain4j.domain.po;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import nonapi.io.github.classgraph.json.Id;
import org.bson.types.ObjectId;
import org.springframework.data.mongodb.core.mapping.Document;


/**
 * MongoDB 对应的实体类 聊天记录表
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
@Document("chat_messages")       // 程序运行后，在mongodb数据库 chat_memory_db 中创建一个名为 chat_messages 的集合
public class ChatMessagesForm {
    @Id
    private ObjectId messageId;  // 唯一标识，映射到 MongoDB 文档的 _id 字段
    private String memoryId;     // 聊天记录的标识，映射到 MongoDB 文档的 memoryId 字段
    private String content;      // 存储聊天记录列表，格式为JSON字符串
}