package com.petos.monitor.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * MQTT 配置属性类。
 * 作用：把 application.yml 里以 mqtt 开头的配置，自动“装”到这个类的字段里，
 * 代码里需要哪个参数直接取字段，不用到处写死。
 *
 * @ConfigurationProperties(prefix = "mqtt")：表示本类字段对应 yml 里 mqtt.xxx 的配置
 * @Component：交给 Spring 管理，别的类才能注入使用
 */
@Component
@ConfigurationProperties(prefix = "mqtt")
public class MqttProperties {

    // EMQX 服务器地址（主机名/IP）
    private String brokerHost;
    // EMQX 端口，TCP 直连用 1883
    private Integer brokerPort;
    // 连接用户名
    private String username;
    // 连接密码
    private String password;
    // 客户端 ID：每个连接必须唯一，固定写死避免多端冲突
    private String clientId;
    // 连接超时时间（秒）
    private Integer connectionTimeout;
    // 心跳保活间隔（秒），多久没消息就发一次心跳维持连接
    private Integer keepAliveInterval;

    // getter / setter
    public String getBrokerHost() {
        return brokerHost;
    }

    public void setBrokerHost(String brokerHost) {
        this.brokerHost = brokerHost;
    }

    public Integer getBrokerPort() {
        return brokerPort;
    }

    public void setBrokerPort(Integer brokerPort) {
        this.brokerPort = brokerPort;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getClientId() {
        return clientId;
    }

    public void setClientId(String clientId) {
        this.clientId = clientId;
    }

    public Integer getConnectionTimeout() {
        return connectionTimeout;
    }

    public void setConnectionTimeout(Integer connectionTimeout) {
        this.connectionTimeout = connectionTimeout;
    }

    public Integer getKeepAliveInterval() {
        return keepAliveInterval;
    }

    public void setKeepAliveInterval(Integer keepAliveInterval) {
        this.keepAliveInterval = keepAliveInterval;
    }
}
