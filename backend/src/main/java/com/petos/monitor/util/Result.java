package com.petos.monitor.util;

import java.io.Serializable;

/**
 * 统一返回结果封装类。
 * 作用：后端所有接口都返回同一个“外壳”格式，前端拿到后能用同一套代码解析，不会因为接口不同而乱套。
 *
 * 固定结构（和前端 request.js 的约定完全一致）：
 * {
 *   "code": 0,            // 状态码：0 表示成功，其它数字表示失败
 *   "message": "成功",    // 提示信息：失败时前端可以直接弹给用户看
 *   "data": {...}         // 真正的业务数据：可能是对象、列表，也可能为 null
 * }
 *
 * @param <T> 泛型：data 里装的数据类型不固定，用 T 表示“任意类型”，提高复用
 * 实现 Serializable：允许这个对象被序列化（网络传输/缓存时需要），照写即可
 */
public class Result<T> implements Serializable {

    // 成功时统一使用的状态码，前端拦截器把 code=0 或 200 都当作成功
    public static final int CODE_SUCCESS = 0;
    // 失败时统一使用的状态码，自定义一个非 0 数字即可
    public static final int CODE_ERROR = 500;

    // 状态码字段：决定前端这次请求算成功还是失败
    private Integer code;
    // 提示信息字段：给人看的说明文字
    private String message;
    // 业务数据字段：真正要返回给前端的数据
    private T data;

    /**
     * 无参构造方法：框架在反序列化时可能需要，先留着
     */
    public Result() {
    }

    /**
     * 全参构造方法：方便下面的静态方法快速组装结果
     *
     * @param code    状态码
     * @param message 提示信息
     * @param data    业务数据
     */
    public Result(Integer code, String message, T data) {
        this.code = code;
        this.message = message;
        this.data = data;
    }

    /**
     * 成功但不带数据（比如只需要告诉前端“操作成功”）
     *
     * @param <T> 任意数据类型
     * @return 组装好的成功 Result，data 为 null
     */
    public static <T> Result<T> success() {
        return new Result<>(CODE_SUCCESS, "成功", null);
    }

    /**
     * 成功并带数据（最常用，查询列表、查详情都走这里）
     *
     * @param data 要返回给前端的业务数据
     * @param <T>  数据的实际类型
     * @return 组装好的成功 Result
     */
    public static <T> Result<T> success(T data) {
        return new Result<>(CODE_SUCCESS, "成功", data);
    }

    /**
     * 失败，只给提示信息
     *
     * @param message 失败原因，会被前端展示
     * @param <T>     任意数据类型
     * @return 组装好的失败 Result，data 为 null
     */
    public static <T> Result<T> fail(String message) {
        return new Result<>(CODE_ERROR, message, null);
    }

    /**
     * 失败，可自定义状态码和提示信息（特殊错误场景用）
     *
     * @param code    自定义错误码
     * @param message 失败原因
     * @param <T>     任意数据类型
     * @return 组装好的失败 Result
     */
    public static <T> Result<T> fail(Integer code, String message) {
        return new Result<>(code, message, null);
    }

    // 下面是三个字段的 getter / setter，手动写出而不用 Lombok，方便零基础同学对照理解
    public Integer getCode() {
        return code;
    }

    public void setCode(Integer code) {
        this.code = code;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public T getData() {
        return data;
    }

    public void setData(T data) {
        this.data = data;
    }
}
