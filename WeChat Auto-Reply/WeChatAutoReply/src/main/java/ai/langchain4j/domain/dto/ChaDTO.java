package ai.langchain4j.domain.dto;

import lombok.Data;

/**
 * 用于接收前端的用户信息
 */
@Data
public class ChaDTO {
    private Long memoryId;//对话id
    private String message;//用户问题
}
