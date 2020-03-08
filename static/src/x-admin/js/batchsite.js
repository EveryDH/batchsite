
    /**
     * 插件交互对象
     * 您的所有JS代码可以写在里面
     * 若不习惯JS的面向对象编程，可删除此对象，使用传统函数化的方式编写
     * */
    var batchsite = {

        // 填充插件的可用安装文件包
        get_domain_list: function () {
            request_plugin("batchsite", "get_domain_list", "", function (rdata) {
                console.log(rdata)
                if (rdata["status"] == "Success") {

                    var redataBody = '';
                    for (var i = 0; i < rdata.data.length; i++) {
                        id = i + 1;
                        redataBody += '<tr>'
                            + '<td>' + id + '</td>'
                            + '<td>' + rdata.data[i].domain + '</td>'
                            + '<td>' + rdata.data[i].second_domain + '</td>'
                            + '<td>' + '<input type="checkbox" class=' + id + '> </td>'
                            + '</tr>'
                    }
                    $("#domain_list").html(redataBody);
                }
            });
        },



        add_site: function (codename, title) {
            var array;
            var str = "";
            var domainlist = '';
            var Webport = [];
            var domain = array = $("#mainDomain").val().split("\n");
            var checkDomain = domain[0].split('.');
            if (checkDomain.length < 1) {
                layer.msg('域名格式不正确，请重新输入!', {icon: 2});
                return;
            }
            for (var i = 1; i < domain.length; i++) {
                domainlist += '"' + domain[i] + '",';
            }
            Webport = domain[0].split(":")[1];//主域名端口
            if (Webport == undefined) {
                Webport = "80";
            }
            domainlist = domainlist.substring(0, domainlist.length - 1);//子域名json
            mainDomain = domain[0].split(':')[0];
            domain = '{"domain":"' + domain[0] + '","domainlist":[' + domainlist + '],"count":' + domain.length + '}';//拼接json
            var php_version = $("select[name='version']").val();
            var loadT = layer.msg('正在创建站点 <img src="/static/img/ing.gif">', {icon: 16, time: 0, shade: [0.3, "#000"]})
            var data = $("#addweb").serialize() + "&port=" + Webport + "&webname=" + domain + '&ftp=false&sql=true&address=localhost&codeing=utf8&version=' + php_version;
            $.post('/site?action=AddSite', data, function (ret) {
                layer.close(loadT)
                if (!ret.siteStatus) {
                    layer.msg(ret.msg, {icon: 5});
                    return;
                }
                layer.close(add)
                var sqlData = '';
                if (ret.databaseStatus) {
                    sqlData = "<p class='p1'>数据库账号资料</p>\
					 		<p><span>数据库名：</span><strong>" + ret.databaseUser + "</strong></p>\
					 		<p><span>用户：</span><strong>" + ret.databaseUser + "</strong></p>\
					 		<p><span>密码：</span><strong>" + ret.databasePass + "</strong></p>\
					 		"
                }
                var pdata = 'dname=' + codename + '&site_name=' + mainDomain + '&php_version=' + php_version;
                var loadT = layer.msg('<div class="depSpeed">正在提交 <img src="/static/img/ing.gif"></div>', {
                    icon: 16,
                    time: 0,
                    shade: [0.3, "#000"]
                });

                setTimeout(function () {
                    GetSpeed();
                }, 2000);

                $.post('/deployment?action=SetupPackage', pdata, function (rdata) {
                    layer.close(loadT)
                    if (!rdata.status) {
                        layer.msg(rdata.msg, {icon: 5, time: 10000});
                        return;
                    }

                    if (rdata.msg.admin_username != '') {
                        sqlData = "<p class='p1'>已成功部署，无需安装，请登录修改默认账号密码</p>\
					 		<p><span>用户：</span><strong>" + rdata.msg.admin_username + "</strong></p>\
					 		<p><span>密码：</span><strong>" + rdata.msg.admin_password + "</strong></p>\
					 		"
                    }
                    sqlData += "<p><span>访问站点：</span><a class='btlink' href='http://" + mainDomain + rdata.msg.success_url + "' target='_blank'>http://" + mainDomain + rdata.msg.success_url + "</a></p>";

                    layer.open({
                        type: 1,
                        area: '600px',
                        title: '已成功部署【' + title + '】',
                        closeBtn: 2,
                        shadeClose: false,
                        content: "<div class='success-msg'>\
						<div class='pic'><img src='/static/img/success-pic.png'></div>\
						<div class='suc-con'>\
							" + sqlData + "\
						</div>\
					 </div>",
                    });
                    if ($(".success-msg").height() < 150) {
                        $(".success-msg").find("img").css({
                            "width": "150px",
                            "margin-top": "30px"
                        });
                    }
                });
            });

        }
    };


    /**
     * 发送请求到插件
     * 注意：除非你知道如何自己构造正确访问插件的ajax，否则建议您使用此方法与后端进行通信
     * @param plugin_name    插件名称 如：demo
     * @param function_name  要访问的方法名，如：get_logs
     * @param args           传到插件方法中的参数 请传入数组，示例：{p:1,rows:10,callback:"demo.get_logs"}
     * @param callback       请传入处理函数，响应内容将传入到第一个参数中
     */
    function request_plugin(plugin_name, function_name, args, callback, timeout) {
        if (!timeout) timeout = 3600;
        $.ajax({
            type: 'POST',
            url: '/plugin?action=a&s=' + function_name + '&name=' + plugin_name,
            data: args,
            timeout: timeout,
            success: function (rdata) {

                if (!callback) {
                    layer.msg(rdata.msg, {icon: rdata.status ? 1 : 2});
                    return;
                }
                return callback(rdata);
            },
            error: function (ex) {
                if (!callback) {
                    layer.msg('请求过程发现错误!', {icon: 2});
                    return;
                }
                return callback(ex);
            }
        });
    }
