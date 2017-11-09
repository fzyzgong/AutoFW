
var url;
//新建用户信息
function newUserInfo(){
    url = '/AutoFW/add_userinfo/';
    $('#dlg_user').dialog('open').dialog('center').dialog('创建','New UserInfo');
    $('#fm_user').form('clear');
}

// 点击SAVE 提交保存
function saveUserInfo(){
           // alert('saveUser:'+url);
   $('#fm_user').form('submit',{
        url: url,
        onSubmit: function(){
            return $(this).form('validate');
        },
        success: function(result){
            if (result=="save"){
               $('#dlg_user').dialog('close');
                $('#dg_user').datagrid('reload');
            }else if(result=="username repeat"){
                $.messager.show({
                    title: 'Error',
                    msg: "用户名重复了!"
                });
            }else if(result=="superman"){
                $.messager.show({
                    title: 'Error',
                    msg: "超级用户不允许删除或修改!"
                });
            }
            else if (result.errorMsg){
                $.messager.show({
                    title: 'Error',
                    msg: result.errorMsg
                });
            }
            else {
                $('#dlg_user').dialog('close');        // close the dialog
                $('#dg_user').datagrid('reload');    // reload the user data
            }
        }
    });
}


function editUserInfo(){
    var row = $('#dg_user').datagrid('getSelected');
    if(row){
        $('#dlg_user').dialog('open').dialog('center').dialog('setTitle','Edit Project API');
        $('#fm_user').form('load',row);
        url = '/AutoFW/edit_userinfo/'+row.username;
    }

}


//删除非superman userinfo
function deleteUserInfo(){
    var row = $('#dg_user').datagrid('getSelected');
    var data = JSON.stringify(row)
    $.messager.confirm('Confirm','Are you sure you want to destroy this user?',function(r){
      if (r){
          $.ajax({
            url: '/AutoFW/remove_userinfo/'+row.username,
            type: 'POST',
            data: {id:row.username},
            success: function(data) {
                if (data=="REMOVE"){
                    $('#dg_user').datagrid('reload');    // reload the user data bug
                }else if(data=="superman"){
                    $.messager.show({
                    title: 'Error',
                    msg: "超级用户不允许删除或修改!"
                    })
                }
            },
            error: function(data) {alert("error")}
         });
      }
    });
}


//重置用户密码(superman除外)
function resetPassword() {
    var row = $('#dg_user').datagrid('getSelected');

    $.messager.confirm('Confirm',"Are you sure ["+row.username+"] reset password?",function(r){
      if (r){
          $.ajax({
            url: '/AutoFW/resetPW_userinfo/'+row.username,
            type: 'POST',
            data: {id:row.username},
            success: function(data) {
                if (data=="success"){
                    $.messager.show({
                    title: '提示',
                    msg: "该用户密码重置成功!"
                    })
                }else if(data=="superman"){
                    $.messager.show({
                    title: 'Error',
                    msg: "超级用户不允许删除或修改!"
                    })
                }
            },
            error: function(data) {alert("error")}
         });
      }
    });
}