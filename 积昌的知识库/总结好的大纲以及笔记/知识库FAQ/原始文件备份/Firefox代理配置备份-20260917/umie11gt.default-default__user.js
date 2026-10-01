// 让 Firefox 走小火箭（Rocket/ClashR）代理 127.0.0.1:4780
// 原因：校园网直接封锁境外站点，Firefox 默认不走 Windows 系统代理（直连）会打不开外网。
// 2026-08-31 由「知识库报错修复」skill 加入。重启 Firefox 后生效。
user_pref("network.proxy.type", 1);
user_pref("network.proxy.http", "127.0.0.1");
user_pref("network.proxy.http_port", 4780);
user_pref("network.proxy.ssl", "127.0.0.1");
user_pref("network.proxy.ssl_port", 4780);
user_pref("network.proxy.share_proxy_settings", true);
user_pref("network.proxy.no_proxies_on", "localhost, 127.0.0.1, ::1");
