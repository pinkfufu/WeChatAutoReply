package ai.langchain4j.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class Knif4jOpenApiConfig {

    @Bean
    public OpenAPI openAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("用户管理接口文档")
                        .description("小智医疗预约智能体")
                        .version("v1.0.0")
                        .contact(new Contact()
                                .name("ZhangYao")
                                .email("yao152990@gmail.com")
                                .url("https://xiaozhi.mikufufu.online/")
                        )
                );
    }
}

