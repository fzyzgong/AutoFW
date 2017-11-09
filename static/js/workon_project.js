//        $(function () {
//            //查询项目模块信息 并动态加入td
//            var table = document.getElementsByClassName("project_attribute_table");
//            var tr = document.getElementById("module_append");
//            var tr2 = document.getElementById("module_append_2");
//            var tr3 = document.getElementById("module_append_3");
//            var project_id = document.getElementById("td_project_id").textContent;
//
//            module_append=$('#module_append');
//            $.get('/AutoFW/module_append/?project_id='+project_id,function (dic) {//{data:[[],[],[]]}
////                alert(dic.data);
//                $.each(dic.data,function (index, item) {//[module_name]
//                    newtd = document.createElement("td");
//                    newtd.innerHTML = item;
//
//                    newtd1 = document.createElement("td");
//                    tr.appendChild(newtd1);
//                    tr.appendChild(newtd);
//
//
//                    newtd2 = document.createElement("td");
//                    newtd3 = document.createElement("td");
//                    newtd2.innerHTML = "test success";
//                    tr2.appendChild(newtd2)
//
//                    tr.appendChild(newtd);
//
//
//                    newtd3.innerHTML = "test failed";
//                    tr2.appendChild(newtd3)
//                })
//            })
//        });

function display_detail(){
    var module_detail = document.getElementById("module_detail");

    if (module_detail.hidden) {
        module_detail.hidden = false;
        document.getElementById("easyui-switchbutton").value = "隐藏模块信息";
      } else  {
        module_detail.hidden = true;
        document.getElementById("easyui-switchbutton").value = "显示模块信息";
      }

}

$('#tt').tabs({
    border:false,
    onSelect:function(title){
        var project_id = document.getElementById("td_project_id").textContent
//                alert(project_id+' is project_id');
        $.get('/AutoFW/project_attribute/?project_id='+project_id, function (data) {
            if(data.project_code = project_id){
                       // alert(data.create_time);
                $("#create_time").html(data.create_time)
                $("#creator").html(data.creator)
                $("#department").html(data.department)
                $("#prioirty").html(data.prioirty)
                $("#project_head_name").html(data.project_name)
                $("#case_count").html(data.project_case_count)
                $("#module_count").html(data.project_module_count)
            }else{
                alert("数据异常，请确认项目编号："+project_id);
            }
        })
    }
});


//模块管理js
var url;
// 显示 编辑框
function newProjectModule(){
    var project_id = document.getElementById("td_project_id").textContent
//            alert('newUser1:'+url);
    url = '/AutoFW/startModule/'+project_id;
//            alert('newUser:'+url);
    $('#dlg').dialog('open').dialog('center').dialog('创建','New Project Module');
    $('#fm').form('clear');

}

//编辑 module
function editProjectModule(){
    var project_id = document.getElementById("td_project_id").textContent
    var row = $('#dg').datagrid('getSelected');
           // alert(row.module_id);
    if (row){
        $('#dlg').dialog('open').dialog('center').dialog('setTitle','Edit Project Module');
        $('#fm').form('load',row);
        //  ajax 编辑USER 并且 通过ajax 保存到后端 SQL
        url = '/AutoFW/editModule/'+row.module_id+'/'+project_id;
//                        alert('editUser:'+url);
    }
}

//getSelected：取得第一个选中行数据，如果没有选中行，则返回 null，否则返回记录。
//getSelections：取得所有选中行数据，返回元素记录的数组数据。
// 根据ID 删除   user
function deleteProjectModule(){
    var row = $('#dg').datagrid('getSelected');
    var data = JSON.stringify(row)
    $.messager.confirm('Confirm','Are you sure you want to destroy this module?',function(r){
      if (r){
          $.ajax({
            url: '/AutoFW/removeModule/',
            type: 'POST',
            data: {id:row.module_id},
            success: function(data) {
                if (data=="REMOVE"){
                    $('#dg').datagrid('reload');    // reload the user data bug
                }
            },
            error: function(data) {alert("error")}
         });
      }
    });
}


// 创建——module 并 SAVE  保存
function saveProjectModule(){
//            alert('saveUser:'+url)
   $('#fm').form('submit',{
        url: url,
        onSubmit: function(){
            return $(this).form('validate');
        },
        success: function(result){
            if (result=="save"){
               $('#dlg').dialog('close');
                $('#dg').datagrid('reload');
            }else
            if (result.errorMsg){
                $.messager.show({
                    title: 'Error',
                    msg: result.errorMsg
                });
            } else {
                $('#dlg').dialog('close');        // close the dialog
                $('#dg').datagrid('reload');    // reload the user data
            }
        }
    });
}

