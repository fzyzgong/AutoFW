$(function () {
    var err_uname=false;
    var err_passwd=false;

    $('#name_input').blur(function () {
        check_username();
    });



    $('#passwd_input').blur(function () {
        check_passwd();
    });


    function check_username() {
        username = $('#name_input').val();
        $.get('/AutoFW/login_check_name/?username='+username, function (data) {
            if(data.count == 1){
                $('#name_input').next().hide();
                err_uname=false;
            }else{
                $('#name_input').next().html('不存在该用户').show();
                err_uname=true;
            }
        })
    }


    function check_passwd() {

        password = $('#passwd_input').val();
        username = $('#name_input').val();

        $.post('/AutoFW/login_check_passwd/',{'password':password,'username':username},function (data) {
            if(data.count == 1){
                $('#passwd_input').next().hide();
                err_passwd=false;
            }else{
                $('#passwd_input').next().html('密码错误').show();
                err_passwd=true;
            }
        });

    }

    document.onkeydown = function (e) {
            if (!e) e = window.event;
            if ((e.keyCode || e.which) == 13) {
                var obtnLogin = document.getElementById("submit_id");   //submit_btn为按钮ID
                obtnLogin.focus();
　　　　　　　　　 fun();//提交按钮触发的方法
            }
        }


    $('#form_input').submit(function () {
        check_username();
        check_passwd();

        if(err_uname == false && err_passwd == false){
            return true;
        }else{
            return false;
        }
    });

})