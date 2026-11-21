package com.petos.monitor.exception;

import com.petos.monitor.util.Result;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.multipart.MaxUploadSizeExceededException;

/**
 * 全局异常处理器。
 * 作用：项目里任何一个 Controller 抛出异常，都会被这里统一接住，
 * 然后返回标准的 Result 外壳，保证前端永远拿到结构一致的 JSON，不会收到一长串报错页面。
 *
 * @RestControllerAdvice：表示这是一个“全局拦截控制器异常”的组件，
 * 它的返回值会自动转成 JSON。
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * 处理我们自己主动抛出的业务异常
     *
     * @ExceptionHandler 告诉 Spring：遇到 BusinessException 就调用这个方法
     */
    @ExceptionHandler(BusinessException.class)
    public Result<Void> handleBusinessException(BusinessException exception) {
        // 把异常里的错误码和提示信息原样返回给前端
        return Result.fail(exception.getCode(), exception.getMessage());
    }

    /**
     * 处理参数校验失败异常（@Valid 校验不通过时抛出）
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result<Void> handleValidException(MethodArgumentNotValidException exception) {
        // 拿到第一条校验错误的提示信息返回，避免信息太多前端不好展示
        String message = exception.getBindingResult().getFieldError() != null
                ? exception.getBindingResult().getFieldError().getDefaultMessage()
                : "参数校验失败";
        return Result.fail(message);
    }

    /**
     * 处理上传文件过大的异常
     */
    @ExceptionHandler(MaxUploadSizeExceededException.class)
    public Result<Void> handleMaxUploadSize(MaxUploadSizeExceededException exception) {
        return Result.fail("上传的图片过大，请压缩后再上传");
    }

    /**
     * 兜底处理：其它所有没预料到的异常统一在这里处理，避免把堆栈信息直接暴露给前端
     */
    @ExceptionHandler(Exception.class)
    public Result<Void> handleException(Exception exception) {
        // 控制台先打印真实异常，方便我们后台排查
        exception.printStackTrace();
        // 给前端一个友好但不暴露细节的提示
        return Result.fail("服务器内部错误，请稍后再试");
    }
}
