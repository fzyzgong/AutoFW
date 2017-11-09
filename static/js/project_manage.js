$(function (){
    $.ajaxSettings({
        beforeSend: function(xhr,settings){
            xhr.setRequestHeader('X-CSRFtoken', $.cookie('csrftoken'))
        }
    })
});

//        $('#dg').datagrid({
//            url:'/booktest/userlist/',
//            columns:[[
//                {field:'Name',title:'name',width:100},
//                {field:'Sex',title:'sex',width:100},
//                {field:'Phone',title:'phone',width:100},
//                {field:'adder',title:'adder',width:100}
//
//　　　　　　　　]]
//        })

var url;
// 显示 编辑框
function newProject(){
           // alert('newUser1:'+url);
    url = '/AutoFW/start/';
//            alert('newUser:'+url);
    $('#dlg').dialog('open').dialog('center').dialog('创建','New Project');
    $('#fm').form('clear');

}

//编辑 USER
function editProject(){
    var row = $('#dg').datagrid('getSelected');
    if (row){
        $('#dlg').dialog('open').dialog('center').dialog('setTitle','Edit Project');
        $('#fm').form('load',row);
        //  ajax 编辑USER 并且 通过ajax 保存到后端 SQL
        url = '/AutoFW/edit/'+row.id;
//                alert('editUser:'+url)
    }
}

// 创建——USER 并 SAVE  保存
function saveProject(){
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

//getSelected：取得第一个选中行数据，如果没有选中行，则返回 null，否则返回记录。
//getSelections：取得所有选中行数据，返回元素记录的数组数据。
// 根据ID 删除   user
function destroyProject(){
    var row = $('#dg').datagrid('getSelected');
    var row1 = $('#dg').datagrid('getSelections');
//            alert(row1[0].id);
//            alert(row1[1].id);
//            alert(row1[2].id);
    var row1total = row1.length;
    var data = JSON.stringify(row1)

    if (row1total > 1){
            $.messager.confirm('Confirm','Are you sure you want to destroy this user?',function(r){
              if (r){
//delete more line
                  for (var i=0;i<row1.length;i++){
            alert(row1[i].id);
                      $.ajax({
                        url: '/AutoFW/remove/',
                        type: 'POST',
                        data: {id:row1[i].id},
//                        headers: {'X-CSRFtoken': $.cookie('csrftoken')},
                        success: function(data) {
                            if (data=="REMOVE"){
                                //bug shuaxin guokuai
                                $('#dg').datagrid('reload');    // reload the user data
                            }
                        },
                        error: function(data) {alert("error")}
                     });
                  }
              }
            });

    }else{
        //sign chose
        if (row){
            $.messager.confirm('Confirm','Are you sure you want to destroy this user?',function(r){
              if (r){
                  $.ajax({
                    url: '/AutoFW/remove/',
                    type: 'POST',
                    data: {id:row.id},
//                        headers: {'X-CSRFtoken': $.cookie('csrftoken')},
                    success: function(data) {
                        if (data=="REMOVE"){
                            $('#dg').datagrid('reload');    // reload the user data
                        }
                    },
                    error: function(data) {alert("error")}
                 });
              }
            });
        }
    }


}

function incomeProject() {
    var row = $('#dg').datagrid('getSelected');
    if(row == null){
        alert("请选择一个项目在点击进入项目");
    }else{
//                alert(row.project_id);
//                url = '/AutoFW/project_'+row.project_id+'/';
        url = '/AutoFW/income_project/'+row.project_id;
        //a标签herf动态地址
        $("#income_project").attr("href",url);
    }
}
