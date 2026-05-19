package ai.langchain4j.domain.po;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

/**
 * Mysql 预约信息实体类
 */

@Data
@TableName("appointment")
@Schema(description = "预约信息实体")
public class Appointment {

    @TableId(type = IdType.AUTO)
    @Schema(description = "主键ID", example = "1")
    private Long id;

    @NotBlank(message = "用户名不能为空")
    @Schema(description = "用户名", example = "张三")
    private String username;

    @NotBlank(message = "身份证号不能为空")
    @Pattern(
            regexp = "^[1-9]\\d{5}(18|19|20)\\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\\d|3[01])\\d{3}[0-9Xx]$",
            message = "身份证号格式不正确"
    )
    @Schema(description = "身份证号", example = "110101199001011234")
    private String idCard;

    @NotBlank(message = "科室不能为空")
    @Schema(description = "科室名称", example = "内科")
    private String department;

    @NotBlank(message = "预约日期不能为空")
    @Pattern(
            regexp = "^\\d{4}-\\d{2}-\\d{2}$",
            message = "日期格式必须为 yyyy-MM-dd"
    )
    @Schema(description = "预约日期", example = "2026-01-20")
    private String date;

    @NotBlank(message = "预约时间不能为空")
    @Pattern(
            regexp = "^\\d{2}:\\d{2}$",
            message = "时间格式必须为 HH:mm"
    )
    @Schema(description = "预约时间", example = "09:30")
    private String time;

    @Schema(description = "医生姓名", example = "李医生")
    private String doctorName;

    @TableLogic
    @Schema(description = "逻辑删除标识：0-未删除，1-已删除", example = "0")
    private Boolean deleted;
}
