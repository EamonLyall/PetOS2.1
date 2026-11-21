package com.petos.monitor.mqtt;

import com.petos.monitor.config.MqttProperties;
import com.petos.monitor.exception.BusinessException;
import org.eclipse.paho.client.mqttv3.MqttCallbackExtended;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import java.nio.charset.StandardCharsets;

/**
 * MQTT 客户端管理器：整个后端和 EMQX 打交道的“总开关”。
 * 职责：建立连接、订阅主题、接收消息并交给业务层、对外提供发布消息的方法。
 *
 * 设计亮点（答辩可讲）：
 * 1. EMQX 没启动时后端照常能起来，定时任务会自动重连，不会因为没开 MQTT 就启动失败；
 * 2. 断线后自动重连，重连成功自动重新订阅主题。
 */
@Component
public class MqttClientManager {

    // 日志对象：比 System.out.println 更规范，能打印时间和级别
    private static final Logger log = LoggerFactory.getLogger(MqttClientManager.class);

    // MQTT 连接参数
    private final MqttProperties mqttProperties;
    // 真正处理消息业务的服务，收到消息后转给它
    private final MqttMessageService mqttMessageService;

    // Paho 提供的 MQTT 客户端对象
    private MqttClient mqttClient;

    /**
     * 构造方法注入依赖（Spring 推荐用构造注入，方便测试、依赖关系清晰）
     */
    public MqttClientManager(MqttProperties mqttProperties,
                             MqttMessageService mqttMessageService) {
        this.mqttProperties = mqttProperties;
        this.mqttMessageService = mqttMessageService;
    }

    /**
     * @PostConstruct：这个 Bean 创建好之后自动执行一次，用来初始化客户端
     */
    @PostConstruct
    public void init() {
        try {
            // 服务器地址，固定用 tcp 协议、1883 端口
            String brokerAddress = "tcp://" + mqttProperties.getBrokerHost()
                    + ":" + mqttProperties.getBrokerPort();
            // MemoryPersistence 表示消息状态存在内存里，不落地文件，最小版本够用
            mqttClient = new MqttClient(brokerAddress,
                    mqttProperties.getClientId(), new MemoryPersistence());
            // 注册回调：连接完成、断线、收到消息都会触发对应方法
            mqttClient.setCallback(new PetosMqttCallback());
            log.info("【MQTT】客户端初始化完成，准备连接 {}", brokerAddress);
        } catch (MqttException e) {
            // 初始化失败先不阻断程序，等定时任务重试
            log.error("【MQTT】客户端初始化失败：{}", e.getMessage());
        }
    }

    /**
     * 定时任务：每 10 秒检查一次，没连上就尝试连接
     * 这样即使先启动后端、后启动 EMQX，也能自动接上
     */
    @Scheduled(fixedDelay = 10000)
    public void tryConnect() {
        try {
            if (mqttClient == null || mqttClient.isConnected()) {
                // 客户端没建好，或者已经连上，就不用处理
                return;
            }
            // 组装连接参数
            MqttConnectOptions options = new MqttConnectOptions();
            options.setUserName(mqttProperties.getUsername());
            options.setPassword(mqttProperties.getPassword().toCharArray());
            options.setConnectionTimeout(mqttProperties.getConnectionTimeout());
            options.setKeepAliveInterval(mqttProperties.getKeepAliveInterval());
            // 开启自动重连，网络抖动时 Paho 自己会尝试恢复
            options.setAutomaticReconnect(true);
            // 清理会话：每次都以全新状态连接，最小版本简单可靠
            options.setCleanSession(true);
            // 发起连接，连接成功后会触发回调 connectComplete，在里面订阅主题
            mqttClient.connect(options);
            log.info("【MQTT】连接 EMQX 成功");
        } catch (MqttException e) {
            // 连不上只打印提示，等下一个 10 秒再试，不影响后端运行
            log.warn("【MQTT】暂时连接失败，等待自动重试：{}", e.getMessage());
        }
    }

    /**
     * 对外发布消息（控制指令就是通过这里发给硬件）
     *
     * @param topic   目标主题
     * @param payload 消息内容（JSON 字符串）
     */
    public void publish(String topic, String payload) {
        if (mqttClient == null || !mqttClient.isConnected()) {
            // 没连上就明确报错，让前端知道指令没发出去
            throw new BusinessException("MQTT 未连接，指令发送失败，请先启动 EMQX");
        }
        try {
            // 把字符串按 UTF-8 转成字节，封装成 MqttMessage
            MqttMessage message = new MqttMessage(payload.getBytes(StandardCharsets.UTF_8));
            message.setQos(1); // QoS=1：至少送达一次，控制指令不能丢
            mqttClient.publish(topic, message);
            log.info("【MQTT】发布消息 主题={} 内容={}", topic, payload);
        } catch (MqttException e) {
            throw new BusinessException("MQTT 消息发布失败：" + e.getMessage());
        }
    }

    /**
     * 内部回调类：定义各种 MQTT 事件发生时怎么处理
     */
    private class PetosMqttCallback implements MqttCallbackExtended {

        /**
         * 连接完成（首次连接和自动重连都会触发）
         *
         * @param reconnect true 表示这是断线后重连，false 表示首次连接
         */
        @Override
        public void connectComplete(boolean reconnect, String serverURI) {
            try {
                // 无论首次还是重连，都统一订阅全部主题（clean session 下重连需重新订阅）
                for (String topic : MqttTopicConstants.ALL_SUBSCRIBE_TOPICS) {
                    mqttClient.subscribe(topic, 1); // QoS=1
                }
                log.info("【MQTT】订阅主题完成，共 {} 个", MqttTopicConstants.ALL_SUBSCRIBE_TOPICS.length);
            } catch (MqttException e) {
                log.error("【MQTT】订阅主题失败：{}", e.getMessage());
            }
        }

        /**
         * 连接断开时触发
         */
        @Override
        public void connectionLost(Throwable cause) {
            // 自动重连已开启，这里只记录日志
            log.warn("【MQTT】连接断开，等待自动重连：{}", cause.getMessage());
        }

        /**
         * 消息“送达完成”时触发：发布的消息被 broker 确认收到后回调
         * 最小版本不需要额外处理，留空实现即可，但接口要求必须实现这个方法
         */
        @Override
        public void deliveryComplete(IMqttDeliveryToken token) {
            log.debug("【MQTT】消息送达完成，消息 ID={}", token.getMessageId());
        }

        /**
         * 收到消息时触发（核心入口）
         *
         * @param topic   消息来自哪个主题
         * @param message 消息对象
         */
        @Override
        public void messageArrived(String topic, MqttMessage message) {
            // 把字节转成字符串，交给业务服务按主题分别处理
            String payload = new String(message.getPayload(), StandardCharsets.UTF_8);
            log.info("【MQTT】收到消息 主题={} 内容={}", topic, payload);
            mqttMessageService.handleMessage(topic, payload);
        }
    }
}
