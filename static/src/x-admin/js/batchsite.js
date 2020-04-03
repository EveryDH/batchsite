/**
 * 插件交互对象
 * 您的所有JS代码可以写在里面
 * 若不习惯JS的面向对象编程，可删除此对象，使用传统函数化的方式编写
 * */
var batchsite = {

    // 填充插件的可用安装文件包
    getDomainList: function () {
        request_plugin("batchsite", "getDomainList", "", function (rdata) {
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
        url:  '/' + plugin_name + '/' + function_name + '.json',
        data: args,
        dataType: "JSON",
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
