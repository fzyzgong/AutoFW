

var url;
function newProjectAPI(){
    var project_id = document.getElementById("project_id_flag").value;
           // alert(project_id);
    url = '/AutoFW/startAPI/'+project_id;
//            alert('newUser:'+url);
    $('#dlg').dialog('open').dialog('center').dialog('创建','New Project API');
    $('#fm').form('clear');
}


// 创建——API 并 SAVE  保存
function saveProjectAPI(username){
            // alert('saveUser:'+url+username);
   $('#fm').form('submit',{
        url: url+'/'+username,
        onSubmit: function(){
            return $(this).form('validate');
        },
        success: function(result){
            if (result=="save"){
               $('#dlg').dialog('close');
                $('#dg_case').datagrid('reload');
                alert("新增接口成功！");
            }else if (result=="error"){
                alert("新增接口失败,请检查数据！");
            }
            // else {
            //     $('#dlg').dialog('close');        // close the dialog
            //     $('#dg_case').datagrid('reload');    // reload the user data
            // }
        }
    });
}


//修改接口
function editProjectAPI(){
    // $('#fm_case_id').attr("disabled","disabled"); //???未生效

    var project_id = document.getElementById("project_id_flag").value;
    var row = $('#dg_case').datagrid('getSelected');

    if(row){
        $('#dlg').dialog('open').dialog('center').dialog('setTitle','Edit Project API');
        $('#fm').form('load',row);
        url = '/AutoFW/editAPI/'+project_id;
    }

}


//删除API
function deleteProjectAPI(){
    var row = $('#dg_case').datagrid('getSelected');
    var data = JSON.stringify(row)
    $.messager.confirm('Confirm','Are you sure you want to destroy this module?',function(r){
      if (r){
          $.ajax({
            url: '/AutoFW/removeAPI/',
            type: 'POST',
            data: {id:row.case_id},
            success: function(data) {
                if (data=="REMOVE"){
                    $('#dg_case').datagrid('reload');    // reload the user data bug
                }
            },
            error: function(data) {alert("error")}
         });
      }
    });
}


//查询接口
function doSearchInterfaceName(){
	$('#dg_case').datagrid('load',{
		case_name: $('#case_name').val()
	});
	//$('#dg_case').datagrid('reload');
}


function uploadFile() {
    var maxsize = 20*1024*1024;//20M 限制最大上传限制
    var errMsg = "上传的附件文件不能超过20M！！！";
    //Jquery转换为dom对象：$("#img")[0].files[0];   其中$("#img")是jquery对象， $("#img")[0]是dom对象
    var uploadFile = $("#uploadFile")[0].files[0];
    var failenem = uploadFile.name;
    //取出上传文件的扩展名
    var index = failenem.lastIndexOf(".");
    var ext = failenem.substr(index+1);

    if(ext != "xlsx"){
        alert("上传的文件格式不对");
        return;
    }

    if(uploadFile==undefined){
         alert("请先选择上传文件");
         return;
     }

    var filesize = uploadFile.size;//单位字节

    if(filesize>=maxsize){
        alert(errMsg);
        return;
    }

    var form = new FormData();
    form.append('uploadFile',uploadFile);

    $.ajax({
        url:"/AutoFW/upload_interface_file/",
        type:"POST",
        data:form,
        processData: false,// 告诉jquery要传输data对象
        contentType: false,// 告诉jquery不需要增加请求头对于contentType的设置
        success: function (data) {
            if(data.status == "success"){
                alert(data.msg);
            }
            else if(data.status == "failed"){
                alert(data.msg);
            }
            else if(data.status == "errorFile"){
                alert(data.msg);
            }
            else if(data.status == "blockOut"){
                alert(data.msg);
            }
        }

    });
}