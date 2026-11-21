package com.petos.monitor.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * 全局跨域配置。
 * 背景：前端运行在 5173 端口、后端在 8080 端口，端口不同属于“跨域”，
 * 浏览器默认会拦截这种请求。这里统一放开，前端才能正常调用后端。
 *
 * 注意：本项目前端用 Vite 代理转发 /api，其实已经规避了跨域；
 * 这里再配一层是为了以后直接访问、或部署到不同机器时也不会被拦，属于双保险。
 */
@Configuration
public class CorsConfig implements WebMvcConfigurer {

    /**
     * 重写跨域注册方法，统一配置规则
     */
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")                       // 对所有接口生效
                .allowedOriginPatterns("*")             // 允许任意来源的请求
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS") // 允许的请求方式
                .allowedHeaders("*")                    // 允许任意请求头
                .allowCredentials(true)                 // 允许携带凭证
                .maxAge(3600);                          // 预检请求缓存 1 小时，减少重复询问
    }
}
