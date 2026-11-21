package com.petos.monitor.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.io.File;

/**
 * Web MVC 配置：把本地磁盘上的图片文件夹“映射”成一个可以通过网址访问的路径。
 * 这样前端 <img src="http://localhost:8080/images/xxx.jpg"> 就能直接读到本地图片。
 */
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    // 图片在磁盘上的保存目录，来自 application.yml 的 app.upload.path
    @Value("${app.upload.path}")
    private String uploadPath;

    // 图片的网址前缀，来自 application.yml 的 app.upload.url-prefix
    @Value("${app.upload.url-prefix}")
    private String urlPrefix;

    /**
     * 注册静态资源映射规则
     */
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // 磁盘目录要以 file 协议、并以斜杠结尾，Spring 才能正确定位
        String diskLocation = "file:" + new File(uploadPath).getAbsolutePath() + File.separator;
        // 把 网址前缀/** 映射到磁盘目录
        registry.addResourceHandler(urlPrefix + "/**").addResourceLocations(diskLocation);
    }
}
