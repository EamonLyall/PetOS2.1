package com.petos.monitor.exception;

/**
 * 自定义业务异常。
 * 作用：当业务规则不满足时（比如图片格式不对、设备不存在），主动抛出这个异常，
 * 再由全局异常处理器统一接住，转成标准的 Result 返回给前端。
 *
 * 继承 RuntimeException：属于运行时异常，不用在方法上强制声明 throws，代码更简洁。
 */
public class BusinessException extends RuntimeException {

    // 错误码，和 Result 里的 code 对应，默认 500
    private Integer code;

    /**
     * 只传错误信息的构造方法（最常用）
     *
     * @param message 错误原因，比如“只允许上传 jpg/png 格式图片”
     */
    public BusinessException(String message) {
        super(message);             // 把信息交给父类保存
        this.code = 500;
    }

    /**
     * 同时指定错误码和错误信息
     *
     * @param code    自定义错误码
     * @param message 错误原因
     */
    public BusinessException(Integer code, String message) {
        super(message);
        this.code = code;
    }

    public Integer getCode() {
        return code;
    }

    public void setCode(Integer code) {
        this.code = code;
    }
}
