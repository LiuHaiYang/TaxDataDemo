$('#totaldata').on('click' ,function (){
    alert("稍等～～合并结束会有提示！")
    $.get('/api/v1/data',function (data) {
        if (data['code'] == 200){
            $('#content').append("<div style=\"display: none;\" id='filename'>"+data['filename']+"</div>");
            alert("合并成功，请点击Export下载！");
        }else{
            alert(data['message']);
        }
    });
});

$('#dataclean').on('click' ,function (){
    alert("稍等～～清理结束会有提示！")
    $.get('/api/v1/shouhedata',function (data) {
        if (data['code'] == 200){
            $('#content').append("<div style=\"display: none;\" id='filename'>"+data['filename']+"</div>");
            alert("合并成功，请点击Export下载清理后的Excel！");
        }else{
            alert(data['message']);
        }
    });
});

$("#export").click(function () {
    var filename = $('#filename').html();
    console.log(filename);
    if (filename == ''){
        alert("请您上传合并数据后导出！");
    }else{
        window.location.href = '/api/v1/exportdata?filename='+filename;
    }
});