$('#totaldata').on('click' ,function (){
    $.get('/api/v1/data',function (data) {
        if (data['code'] == 200){
            $('#content').append("<div style=\"display: none;\" id='filename'>"+data['filename']+"</div>");
            alert("合成成功，请下载！");
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